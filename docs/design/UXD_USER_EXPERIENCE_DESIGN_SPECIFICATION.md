# User Experience Design Specification (UXD) — Empório da Música AI Agent

> **Projeto / Sistema:** Empório da Música AI Agent (Desafio Técnico AI Engineer — Artefact)  
> **Status:** Consolidado (Escopo Conversacional CLI & Web UI)  
> **Data:** 2026-11-02  

---

## 1. Diretrizes de UX Conversacional & Persona (Seção 7 do Manual)
- **Tom de Voz:** Informal, acolhedor, mas profissional — *"como se estivesse conversando com um amigo que entende de música"*.
- **Fluxo de Atendimento em 5 Etapas (Seção 7.2):**
  1. **Saudação:** Cumprimentar o cliente pelo nome (quando disponível) e oferecer ajuda.
  2. **Entendimento:** Identificar a intenção (catálogo, preço, rastreamento, troca/devolução, reclamação).
  3. **Consulta:** Acionar silenciosamente e com transparência as Tools determinísticas do sistema.
  4. **Resposta:** Apresentar opções escaneáveis (listas com marcadores, preços originais vs. promocionais, valor no PIX e parcelamento).
  5. **Fechamento:** Perguntar se pode ajudar em algo mais e encerrar com cordialidade.

---

## 2. Interfaces de Interação (Dual UI)
1. **CLI Interativa (`main.py` — Rich Terminal):**
   - Painel de boas-vindas com identidade visual da Empório da Música (`Sua música começa aqui.`).
   - Comandos rápidos: `/limpar` (nova sessão), `/exemplos` (executar os cenários de demonstração), `/sair`.
   - Exibição opcional das Tools acionadas em cada turno (`[Tool Call Trace]`).
2. **Web UI Simples (`app.py` — Streamlit):**
   - Chat estilo mensageiro (`st.chat_message` / `st.chat_input`).
   - Barra lateral com botões de *Quick Prompts* para testar com 1 clique os cenários sugeridos no PDF da Artefact e casos de borda (homônimos, itens sem estoque, promoção ativa vs. expirada, acessórios).
   - Expansor `🔍 Rastreabilidade de Ferramentas (Tool Calls)` em cada resposta do agente para auditoria imediata da banca avaliadora.
