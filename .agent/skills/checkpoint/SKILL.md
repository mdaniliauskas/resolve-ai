# Skill: checkpoint

## Quando usar
- Ao fim de qualquer sessão produtiva (entrega, deploy, decisão importante)
- Quando o contexto estiver acima de ~60% ou a sessão for longa
- Quando o usuário pedir explicitamente para documentar o estado
- **Proativamente**, antes de encerrar, sempre que houver tarefas pendentes

## O que fazer

1. **Atualizar `SESSION_STATE.md`** na raiz do projeto com:
   - Data da sessão
   - O que foi entregue (bullets concisos)
   - URLs, IDs, nomes de serviços relevantes
   - Último commit (hash + mensagem)
   - Próximas tarefas em ordem de prioridade
   - Decisões em aberto que afetam o próximo passo
   - Como retomar (3 linhas máximo)
   - Arquivos críticos alterados

2. **Commitar** o `SESSION_STATE.md` junto com qualquer doc pendente:
   ```
   git add SESSION_STATE.md [outros docs]
   git commit -m "docs: session checkpoint — [resumo do que foi feito]"
   git push
   ```

## Formato do SESSION_STATE.md

```markdown
# Session State — [Projeto]

> Checkpoint gerado em [DATA]. Próxima sessão começa aqui.

## Estado em: [DATA]

### O que foi entregue
- ...

### URLs / IDs de produção
| Serviço | URL/ID |

### Git — último commit
[hash] [mensagem]

## Próxima sessão: [Sprint/Fase]

### Tarefas pendentes
- [ ] ...

### Decisões em aberto
| ADR | Decisão | Prazo |

### Como retomar
1. ...
```

## Regra de ouro
**SESSION_STATE.md é a memória da máquina, não do humano.**
Escreva para o próximo Claude que vai ler frio, sem contexto.
