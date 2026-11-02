"""Structured Knowledge Base for Empório da Música Store Policies (políticas_da_loja.pdf)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pypdf import PdfReader

from src.config import POLICY_PDF_PATH
from src.domain.models import PolicySection
from src.domain.rules import normalize_text

# Canonical semantic sections faithfully representing Version 2.1 (June 2025) of data/políticas_da_loja.pdf
CANONICAL_POLICY_SECTIONS: dict[str, PolicySection] = {
    "geral_sobre_loja": PolicySection(
        topic_key="geral_sobre_loja",
        section_number="1",
        title="1. Sobre a Empório da Música & Dados da Empresa",
        content=(
            "A Empório da Música é uma loja especializada em instrumentos musicais, fundada em 2008 em "
            "Campo Grande, Mato Grosso do Sul. Com mais de 15 anos de atuação no mercado, é referência "
            "regional na venda de instrumentos para músicos iniciantes, intermediários e profissionais. "
            "Slogan: 'Sua música começa aqui.'\n"
            "Catálogo: Abrange mais de 300 instrumentos de marcas nacionais e internacionais (guitarras, "
            "baixos, violões, baterias, teclados, instrumentos de sopro, cordas orquestrais e ukuleles).\n"
            "ESCOPO ESTRITO: Trabalhamos exclusivamente com instrumentos musicais — NÃO comercializamos "
            "acessórios como cordas avulsas, palhetas, cabos, cases, pedais ou amplificadores.\n"
            "Missão (1.1): Democratizar o acesso a instrumentos musicais de qualidade na região Centro-Oeste, "
            "oferecendo atendimento especializado e preços competitivos.\n"
            "Dados da Empresa (1.2):\n"
            "- Razão Social: Empório da Música Instrumentos Musicais Ltda.\n"
            "- Nome Fantasia: Empório da Música\n"
            "- CNPJ: 12.345.678/0001-90\n"
            "- Endereço: Rua 14 de Maio, 3200 — Centro, Campo Grande - MS, CEP 79202-333\n"
            "- Telefone / WhatsApp Geral: (67) 3341-4444 | Canal WhatsApp Atendimento: (67) 3321-4500\n"
            "- E-mail: contato@emporiodamusica.com.br\n"
            "- Fundação: 2008 (Manual Versão 2.1 — Junho de 2025)"
        ),
        key_rules=[
            "Endereço: Rua 14 de Maio, 3200 — Centro, Campo Grande - MS, CEP 79202-333.",
            "Contatos: Telefone (67) 3341-4444 / WhatsApp (67) 3321-4500 / E-mail contato@emporiodamusica.com.br.",
            "Venda exclusiva de instrumentos musicais; proibido vender acessórios (cordas, palhetas, cabos, cases, pedais, amplificadores).",
        ],
    ),
    "horario_funcionamento": PolicySection(
        topic_key="horario_funcionamento",
        section_number="2",
        title="2. Horário de Funcionamento",
        content=(
            "O atendimento presencial na loja e o atendimento via WhatsApp seguem os mesmos horários:\n"
            "- Segunda a Sexta-feira: 09:00 às 18:00\n"
            "- Sábado: 09:00 às 13:00\n"
            "- Domingo e Feriados: Fechado (respostas automáticas fora do expediente informando horário de retorno).\n"
            "Em datas especiais (Black Friday, Aniversário da Loja, Natal), o horário pode ser estendido, "
            "com comunicação prévia nas redes sociais e no WhatsApp."
        ),
        key_rules=[
            "Segunda a Sexta-feira: 09:00 às 18:00.",
            "Sábado: 09:00 às 13:00.",
            "Domingo e Feriados: Fechado.",
        ],
    ),
    "formas_pagamento_parcelamento": PolicySection(
        topic_key="formas_pagamento_parcelamento",
        section_number="3",
        title="3. Formas de Pagamento e Regras de Parcelamento",
        content=(
            "Formas de pagamento aceitas para compras presenciais e online:\n"
            "- PIX: Pagamento à vista com 5% de desconto sobre o preço de tabela (não cumulativo com promoções ativas).\n"
            "- Cartão de Débito: Pagamento à vista (todas as bandeiras aceitas).\n"
            "- Cartão de Crédito: Até 12x sem juros (respeitando as regras de parcela mínima por faixa).\n"
            "- Boleto Bancário: Pagamento à vista (compensação em até 3 dias úteis).\n\n"
            "Regras de Parcelamento (3.1):\n"
            "- Parcelamento em até 3x: sem juros, parcela mínima de R$ 50,00 (exceto compras abaixo de R$ 50,00 à vista).\n"
            "- Parcelamento de 4x a 6x: sem juros, parcela mínima de R$ 80,00.\n"
            "- Parcelamento de 7x a 12x: sem juros, parcela mínima de R$ 100,00.\n"
            "- Combinação de formas de pagamento (ex.: PIX + cartão): permitida para compras acima de R$ 2.000,00."
        ),
        key_rules=[
            "PIX: 5% de desconto sobre o preço de tabela (não cumulativo com promoções).",
            "Parcelamento sem juros: 1x-3x (mín. R$ 50), 4x-6x (mín. R$ 80), 7x-12x (mín. R$ 100).",
            "Pagamento combinado (PIX + cartão): permitido apenas para compras acima de R$ 2.000,00.",
            "Boleto bancário: à vista, compensação em até 3 dias úteis.",
        ],
    ),
    "trocas_devolucoes_arrependimento": PolicySection(
        topic_key="trocas_devolucoes_arrependimento",
        section_number="4",
        title="4. Política de Trocas e Devoluções (CDC Lei nº 8.078/90)",
        content=(
            "4.1 Direito de Arrependimento (Compras Online):\n"
            "- Prazo: até 7 (sete) dias corridos após o recebimento do produto, sem necessidade de justificativa.\n"
            "- Condição: produto em sua embalagem original, sem sinais de uso, com todos os acessórios e manuais.\n"
            "- Reembolso: realizado na mesma forma de pagamento original em até 10 dias úteis.\n"
            "- Frete de devolução: por conta da loja em caso de arrependimento.\n\n"
            "4.2 Trocas por Defeito:\n"
            "- Defeito de fabricação: troca direta na loja em até 30 (trinta) dias corridos após a compra.\n"
            "- Após 30 dias: acionar a garantia diretamente com o fabricante (a Empório da Música pode intermediar mediante solicitação).\n"
            "- Exclusões: danos por mau uso, quedas, exposição a umidade excessiva ou modificações não autorizadas não são cobertos.\n\n"
            "4.3 Trocas por Preferência:\n"
            "- Trocas por cor, modelo ou tamanho: permitidas em até 7 dias, mediante disponibilidade do produto desejado.\n"
            "- Condição: produto em perfeito estado e na embalagem original; diferenças de valor serão cobradas ou reembolsadas.\n\n"
            "4.4 Itens Não Elegíveis para Troca:\n"
            "- Instrumentos com personalização ou ajustes sob encomenda (setup, regulagem especial).\n"
            "- Produtos adquiridos em promoções de liquidação com aviso explícito de 'venda final'.\n"
            "- Boquilhas de instrumentos de sopro, por questões de higiene."
        ),
        key_rules=[
            "Direito de Arrependimento (online): até 7 dias corridos do recebimento, sem uso, frete pela loja, reembolso em até 10 dias úteis.",
            "Troca por Defeito: até 30 dias corridos da compra na loja; após 30 dias, garantia com o fabricante.",
            "Troca por Preferência: até 7 dias em perfeito estado e embalagem original.",
            "Inelegíveis: personalizados/setup sob encomenda, liquidação 'venda final' e boquilhas de sopro.",
        ],
    ),
    "frete_entregas_rastreamento": PolicySection(
        topic_key="frete_entregas_rastreamento",
        section_number="5",
        title="5. Política de Frete, Entregas e Código de Rastreamento",
        content=(
            "5.1 Entregas na Região Metropolitana de Campo Grande:\n"
            "- Frete grátis para pedidos acima de R$ 500,00.\n"
            "- Para pedidos abaixo de R$ 500,00: taxa fixa de R$ 35,00.\n"
            "- Prazo de entrega: 1 a 3 dias úteis.\n"
            "- Entrega realizada por motoboy próprio (cliente é contactado por telefone antes da entrega).\n\n"
            "5.2 Entregas para Outras Cidades:\n"
            "- PAC (Correios): 5 a 12 dias úteis | Rastreamento: Sim | Seguro: Incluído.\n"
            "- SEDEX (Correios): 2 a 5 dias úteis | Rastreamento: Sim | Seguro: Incluído.\n"
            "- Jadlog (.package): 3 a 8 dias úteis | Rastreamento: Sim | Seguro: Incluído.\n"
            "- Valor calculado conforme CEP, peso e dimensões. Instrumentos de grande porte (baterias acústicas, pianos digitais, contrabaixos) podem exigir frete especial com cotação individual.\n"
            "- Todos os envios incluem seguro contra extravios e danos. Em caso de avaria, o cliente deve recusar o recebimento e contatar imediatamente a loja.\n\n"
            "5.3 Código de Rastreamento:\n"
            "- Enviado automaticamente por e-mail e WhatsApp após o despacho.\n"
            "- Formato padrão: BR seguido de 9 caracteres alfanuméricos e BR (ex.: BR4K7M2X9P1BR)."
        ),
        key_rules=[
            "Campo Grande/Região Metropolitana: Grátis acima de R$ 500,00; R$ 35,00 até R$ 500,00; 1 a 3 dias úteis via motoboy próprio.",
            "Outras cidades: PAC (5-12 dias úteis), SEDEX (2-5 dias úteis), Jadlog (3-8 dias úteis) — todos com seguro e rastreamento.",
            "Grande porte (baterias acústicas, pianos digitais, contrabaixos): pode exigir frete especial com cotação individual.",
        ],
    ),
    "promocoes_descontos": PolicySection(
        topic_key="promocoes_descontos",
        section_number="6",
        title="6. Promoções e Descontos",
        content=(
            "6.1 Principais Campanhas:\n"
            "- Aniversário da Loja (Agosto): 10% a 25% em itens selecionados.\n"
            "- Black Friday (Novembro): 15% a 30% em todo o catálogo.\n"
            "- Volta às Aulas (Fevereiro): descontos em instrumentos para estudantes.\n"
            "- Queima de Estoque: promoções pontuais para renovação de catálogo.\n"
            "- Semana do Músico (22 de novembro): promoções especiais.\n\n"
            "6.2 Regras de Promoções:\n"
            "- Cumulatividade: promoções NÃO são cumulativas. O desconto de PIX (5%) NÃO se aplica sobre preços já promocionais.\n"
            "- Estoque: sujeitas à disponibilidade. Produtos esgotados não geram direito a rain check (reserva de preço).\n"
            "- Comunicação: preços promocionais devem sempre ser apresentados junto ao preço original e ao percentual de desconto."
        ),
        key_rules=[
            "Não-cumulatividade: desconto de 5% no PIX NÃO se aplica sobre produtos com promoção ativa.",
            "Transparência obrigatória: sempre informar Preço Original, % de Desconto e Preço Promocional.",
            "Promoções expiradas: nunca prometer desconto vencido; informar com transparência o preço atual.",
        ],
    ),
    "atendimento_whatsapp_escopo": PolicySection(
        topic_key="atendimento_whatsapp_escopo",
        section_number="7",
        title="7. Diretrizes de Atendimento via WhatsApp e Situações Especiais",
        content=(
            "7.1 Diretrizes:\n"
            "- Tom de voz: informal mas profissional ('como se estivesse conversando com um amigo que entende de música').\n"
            "- Tempo de resposta: máximo de 5 minutos no expediente.\n"
            "- Informações precisas: nunca fornecer preços, estoque ou prazos sem consultar o sistema.\n"
            "- Escopo: exclusivamente instrumentos musicais. Redirecionar educadamente pedidos de acessórios (cordas, cabos, palhetas, pedais, amplificadores, cases) e sugerir lojas parceiras.\n\n"
            "7.2 Fluxo Padrão: 1. Saudação -> 2. Entendimento -> 3. Consulta -> 4. Resposta -> 5. Fechamento.\n\n"
            "7.3 Situações Especiais:\n"
            "- Produto fora de estoque: informar indisponibilidade temporária e sugerir alternativas disponíveis.\n"
            "- Produto descontinuado: informar que não faz mais parte do catálogo e oferecer equivalentes/sucessores.\n"
            "- Promoção expirada: verificar se está ativa; se vencida, informar com transparência e mostrar preço atual.\n"
            "- Reclamação: ouvir com empatia, registrar e encaminhar ao responsável com prazo de retorno de 24 horas úteis."
        ),
        key_rules=[
            "Tom de amigo que entende de música; nunca inventar dados sem consultar o sistema.",
            "Sugerir alternativas disponíveis para produtos fora de estoque ou descontinuados.",
            "Reclamações e dúvidas de gerência: registrar e informar prazo de retorno de 24 horas úteis.",
        ],
    ),
    "garantia": PolicySection(
        topic_key="garantia",
        section_number="8",
        title="8. Garantia Legal e do Fabricante",
        content=(
            "8.1 Garantia Legal (CDC): Todos os produtos possuem garantia legal de 90 (noventa) dias contra "
            "defeitos de fabricação, contados a partir da data de recebimento pelo cliente.\n"
            "8.2 Garantia do Fabricante: Além da garantia legal, a maioria dos fabricantes oferece garantia "
            "própria de 6 meses a 2 anos (detalhada no certificado que acompanha o produto).\n"
            "8.3 O que NÃO Cobre a Garantia:\n"
            "- Desgaste natural de peças (trastes, cordas, feltros, palhetas de sopro).\n"
            "- Danos por mau uso, queda, exposição a condições climáticas extremas.\n"
            "- Modificações ou reparos realizados por terceiros não autorizados.\n"
            "- Danos estéticos que não afetem a funcionalidade do instrumento."
        ),
        key_rules=[
            "Garantia Legal CDC: 90 dias contra defeitos de fabricação a partir do recebimento.",
            "Garantia do Fabricante: 6 meses a 2 anos conforme certificado.",
            "Exclusões: desgaste natural (cordas, trastes, feltros, palhetas), mau uso, quedas, clima extremo, reparos não autorizados e danos estéticos.",
        ],
    ),
    "privacidade_lgpd": PolicySection(
        topic_key="privacidade_lgpd",
        section_number="9",
        title="9. Privacidade, Proteção de Dados (LGPD) e 10. Disposições Finais",
        content=(
            "9. LGPD (Lei nº 13.709/2018): Os dados pessoais coletados no atendimento (nome, telefone, e-mail, "
            "endereço) são utilizados exclusivamente para:\n"
            "- Processamento e entrega de pedidos.\n"
            "- Comunicação sobre status de pedidos e rastreamento.\n"
            "- Envio de promoções e novidades (mediante consentimento explícito).\n"
            "- Cumprimento de obrigações legais e fiscais.\n"
            "Dados não são compartilhados com terceiros para marketing. O cliente pode solicitar a exclusão de "
            "seus dados a qualquer momento pelo WhatsApp ou e-mail.\n\n"
            "10. Disposições Finais: Em caso de dúvidas sobre a aplicação de qualquer política, o atendente "
            "deve consultar a gerência antes de fornecer informações ao cliente."
        ),
        key_rules=[
            "Conformidade estrita com a LGPD (Lei nº 13.709/2018); zero compartilhamento com terceiros para marketing.",
            "Direito de exclusão de dados a qualquer momento via WhatsApp ou e-mail.",
            "Em caso de dúvida sobre política, consultar a gerência antes de responder.",
        ],
    ),
}


class PolicyKnowledgeBase:
    """Loads and serves store policy rules from políticas_da_loja.pdf and canonical sections."""

    def __init__(self, pdf_path: Path = POLICY_PDF_PATH) -> None:
        self.pdf_path = pdf_path
        self.raw_pdf_pages: list[str] = self._extract_pdf_pages()

    def _extract_pdf_pages(self) -> list[str]:
        """Extract raw text pages from the PDF file if available."""
        if not self.pdf_path.exists():
            return []
        try:
            reader = PdfReader(str(self.pdf_path))
            return [page.extract_text() or "" for page in reader.pages]
        except (OSError, ValueError, RuntimeError):
            return []

    def lookup(self, topic: str) -> dict[str, Any]:
        """Retrieve a specific policy section or all sections if 'todas' is requested."""
        norm_topic = normalize_text(topic)

        if norm_topic == "todas" or norm_topic not in CANONICAL_POLICY_SECTIONS:
            # Keyword matching if free-text topic was passed
            matched_sections = []
            for key, sec in CANONICAL_POLICY_SECTIONS.items():
                if norm_topic != "todas" and (
                    norm_topic in normalize_text(key)
                    or norm_topic in normalize_text(sec.title)
                    or norm_topic in normalize_text(sec.content)
                ):
                    matched_sections.append(sec.model_dump())

            if not matched_sections:
                matched_sections = [s.model_dump() for s in CANONICAL_POLICY_SECTIONS.values()]

            return {
                "manual_version": "Versão 2.1 — Junho de 2025",
                "pdf_loaded_pages": len(self.raw_pdf_pages),
                "sections": matched_sections,
            }

        section = CANONICAL_POLICY_SECTIONS[norm_topic]
        return {
            "manual_version": "Versão 2.1 — Junho de 2025",
            "pdf_loaded_pages": len(self.raw_pdf_pages),
            "sections": [section.model_dump()],
        }
