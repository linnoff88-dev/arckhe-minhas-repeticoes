import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent))
sys.path.insert(0, str(AQUI))
import repeticoes as r  # noqa: E402
from gerar_dados import gerar  # noqa: E402


class Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp())
        gerar(cls.tmp)
        cls.m = r.Medidas()
        r.ler_claude(cls.tmp / "claude", 0, cls.m)
        r.ler_codex(cls.tmp / "codex", 0, cls.m)
        cls.res = r.calcula(cls.m)
        cls.N = cls.res["numeros"]


class TestLeitura(Base):
    def test_conta_so_o_que_voce_digitou(self):
        # 5 situaçêo + 3 portal + 3 skill + 3 sim + 1 única + 3 /prime = 18 no Claude; + 1 no Codex
        self.assertEqual(sum(1 for p in self.m.pedidos if p.fonte == "claude"), 18)
        self.assertEqual(sum(1 for p in self.m.pedidos if p.fonte == "codex"), 1)

    def test_robos_fora_e_contados(self):
        self.assertEqual(self.N["turnos_automaticos"]["claude"], 5)   # 4 claude -p + 1 notificaçêo
        self.assertEqual(self.N["turnos_automaticos"]["codex"], 1)

    def test_subagente_e_clear_nao_entram(self):
        self.assertFalse(any("/clear" in p.texto for p in self.m.pedidos))

    def test_sessao_retomada_nao_duplica(self):
        self.assertEqual(sum(1 for p in self.m.pedidos if p.texto.lower().startswith("qual")), 5)

    def test_modelo_e_esforco(self):
        self.assertEqual(self.N["modelo"]["claude-fable-5-2"], 3)
        self.assertEqual(self.N["esforco"]["claude-fable-5-2|xhigh"], 3)
        self.assertEqual(self.N["esforco"]["gpt-6-astra|high"], 1)

    def test_limite_mesma_batida_conta_uma(self):
        self.assertEqual(self.N["limites"], {"session": 1, "weekly": 1, "codex": 1})

    def test_turno_longo(self):
        self.assertEqual(self.N["turnos_mais_de_10min"], {"claude-fable-5-2": 3})


class TestAgrupamento(Base):
    def test_erro_de_digitacao_junta(self):
        g = [x for x in self.res["repetidos"] if "situ" in r.forma_comum(x).lower()]
        self.assertEqual(len(g), 1)
        self.assertEqual(len(g[0]), 5)

    def test_classes(self):
        cl = {r.classifica(g): len(g) for g in self.res["repetidos"]}
        self.assertEqual(cl.get("resposta"), 3)       # sim sim sim
        self.assertEqual(cl.get("checagem"), 5)       # qual a situaçêo (com erro de digitaçêo)
        self.assertEqual(cl.get("skill"), 3)          # o pedido longo de vários passos
        self.assertEqual(cl.get("ja-e-atalho"), 3)    # /prime
        self.assertIn("atalho", cl)

    def test_portal_junta_codex_e_claude(self):
        g = [x for x in self.res["repetidos"] if r.forma_comum(x).startswith("publi")]
        self.assertEqual(len(g), 1)
        self.assertEqual({p.fonte for p in g[0]}, {"claude", "codex"})

    def test_unico_nao_e_repeticao(self):
        self.assertFalse(any("gráficos" in r.forma_comum(g) for g in self.res["repetidos"]))

    def test_porcentagem(self):
        self.assertEqual(self.N["pedidos_seus"], 19)
        self.assertEqual(self.N["pct_repeticao"], round(100 * 18 / 19, 1))


class TestSaida(Base):
    def test_cli_gera_arquivos_e_numeros_sem_texto(self):
        out = self.tmp / "saida"
        p = subprocess.run([sys.executable, str(AQUI.parent / "repeticoes.py"), "--claude", str(self.tmp / "claude"),
                            "--codex", str(self.tmp / "codex"), "--dias", "100000", "--saida", str(out)],
                           capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stderr)
        for f in ["relatorio.html", "relatorio.md", "atalhos.md", "atalhos-espanso.yml", "numeros.json"]:
            self.assertTrue((out / f).is_file(), f)
        self.assertTrue(any((out / "skills-rascunho").iterdir()))
        nums = (out / "numeros.json").read_text()
        for segredo in ["situa", "portal", "repo", "sim", "gráficos"]:
            self.assertNotIn(segredo, nums.lower(), f"numeros.json vazou texto: {segredo}")
        yml = (out / "atalhos-espanso.yml").read_text()
        self.assertNotIn("situ", yml.lower())   # checagem nêo vira atalho
        self.assertEqual(yml.count("trigger:"), len(set(l for l in yml.splitlines() if "trigger:" in l)))

    def test_sem_dados_sai_2(self):
        vazio = self.tmp / "vazio"
        vazio.mkdir(exist_ok=True)
        self.assertEqual(r.main(["--claude", str(vazio), "--codex", str(vazio), "--saida", str(self.tmp / "x")]), 2)

    def test_dias_filtra_por_data_do_arquivo(self):
        f = next((self.tmp / "claude").glob("*/sessao1.jsonl"))
        velho = time.time() - 90 * 86400
        os.utime(f, (velho, velho))
        m = r.Medidas()
        r.ler_claude(self.tmp / "claude", time.time() - 30 * 86400, m)
        self.assertEqual(len([p for p in m.pedidos if "portal" in p.texto]), 0)
        os.utime(f, None)


if __name__ == "__main__":
    unittest.main()
