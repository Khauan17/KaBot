
import os
from supabase import create_client, Client
from datetime import datetime, timedelta
import json

class SistemaMemoria:
    def __init__(self):
        self.supabase: Client = create_client(
            os.getenv('SUPABASE_URL'),
            os.getenv('SUPABASE_KEY')
        )
    
    async def inicializar_bd(self):
        """Inicializa as tabelas necessárias no banco de dados"""
        try:
            # Criar tabela de memória de curto prazo (mensagens brutas)
            # Nota: Em produção, isso seria feito via migrations do Supabase
            print("📊 Verificando estrutura do banco de dados...")
            
            # Testar conexão
            response = self.supabase.table('mensagens_brutas').select('*').limit(1).execute()
            print("✅ Conexão com Supabase estabelecida!")
            
        except Exception as e:
            print(f"⚠️  Aviso: {e}")
            print("💡 Certifique-se de criar as tabelas no Supabase:")
            print("   - mensagens_brutas (id, canal_id, usuario_id, conteudo, timestamp)")
            print("   - memoria_longo_prazo (id, data, resumo, relevancia, timestamp)")
    
    async def salvar_mensagem(self, message):
        """Salva mensagem na memória de curto prazo"""
        try:
            data = {
                'canal_id': str(message.channel.id),
                'usuario_id': str(message.author.id),
                'usuario_nome': message.author.display_name,
                'conteudo': message.content,
                'timestamp': message.created_at.isoformat(),
                'servidor_id': str(message.guild.id) if message.guild else None
            }
            
            result = self.supabase.table('mensagens_brutas').insert(data).execute()
            return True
            
        except Exception as e:
            print(f"❌ Erro ao salvar mensagem: {e}")
            return False
    
    async def processar_memoria_diaria(self):
        """Processa mensagens do dia e cria resumo (sem IA por enquanto)"""
        try:
            # Obter mensagens das últimas 24 horas
            ontem = (datetime.now() - timedelta(days=1)).isoformat()
            
            response = self.supabase.table('mensagens_brutas').select('*').gte('timestamp', ontem).execute()
            mensagens = response.data
            
            if not mensagens:
                print("📝 Nenhuma mensagem para processar hoje.")
                return
            
            # Criar resumo simples (sem IA por enquanto)
            resumo = self.criar_resumo_simples(mensagens)
            
            # Salvar na memória de longo prazo
            await self.salvar_memoria_longo_prazo(resumo)
            
            # Limpar mensagens brutas antigas (mais de 2 dias)
            dois_dias_atras = (datetime.now() - timedelta(days=2)).isoformat()
            self.supabase.table('mensagens_brutas').delete().lt('timestamp', dois_dias_atras).execute()
            
            print(f"✅ Processamento diário concluído. {len(mensagens)} mensagens processadas.")
            
        except Exception as e:
            print(f"❌ Erro no processamento diário: {e}")
    
    def criar_resumo_simples(self, mensagens):
        """Cria um resumo simples das mensagens (placeholder para IA futura)"""
        total_mensagens = len(mensagens)
        usuarios_ativos = len(set(msg['usuario_id'] for msg in mensagens))
        canais_ativos = len(set(msg['canal_id'] for msg in mensagens))
        
        # Palavras mais comuns (análise básica)
        palavras_comuns = {}
        for msg in mensagens:
            palavras = msg['conteudo'].lower().split()
            for palavra in palavras:
                if len(palavra) > 3:  # Ignorar palavras muito curtas
                    palavras_comuns[palavra] = palavras_comuns.get(palavra, 0) + 1
        
        top_palavras = sorted(palavras_comuns.items(), key=lambda x: x[1], reverse=True)[:5]
        
        resumo = f"""📊 Atividade do dia ({datetime.now().strftime('%d/%m/%Y')}):
        
• {total_mensagens} mensagens enviadas
• {usuarios_ativos} usuários participaram das conversas
• {canais_ativos} canais tiveram atividade

🔤 Tópicos mais discutidos: {', '.join([palavra for palavra, _ in top_palavras])}

💬 A comunidade esteve ativa e engajada nas discussões."""
        
        return resumo
    
    async def salvar_memoria_longo_prazo(self, resumo):
        """Salva resumo na memória de longo prazo"""
        try:
            data = {
                'data': datetime.now().strftime('%Y-%m-%d'),
                'resumo': resumo,
                'relevancia': 1.0,  # Placeholder para futura classificação de relevância
                'timestamp': datetime.now().isoformat()
            }
            
            result = self.supabase.table('memoria_longo_prazo').insert(data).execute()
            return True
            
        except Exception as e:
            print(f"❌ Erro ao salvar memória de longo prazo: {e}")
            return False
    
    async def obter_memorias_recentes(self, limite=5):
        """Obtém as memórias mais recentes"""
        try:
            response = self.supabase.table('memoria_longo_prazo').select('*').order('timestamp', desc=True).limit(limite).execute()
            return response.data
        except Exception as e:
            print(f"❌ Erro ao obter memórias: {e}")
            return []
    
    async def buscar_memorias_relacionadas(self, texto, limite=3):
        """Busca memórias relacionadas ao texto (busca simples por enquanto)"""
        try:
            # Busca simples por palavras-chave
            palavras = texto.lower().split()
            memorias = []
            
            response = self.supabase.table('memoria_longo_prazo').select('*').order('timestamp', desc=True).limit(20).execute()
            todas_memorias = response.data
            
            for memoria in todas_memorias:
                resumo_lower = memoria['resumo'].lower()
                relevancia = sum(1 for palavra in palavras if palavra in resumo_lower and len(palavra) > 3)
                
                if relevancia > 0:
                    memoria['relevancia_busca'] = relevancia
                    memorias.append(memoria)
            
            # Ordenar por relevância
            memorias.sort(key=lambda x: x['relevancia_busca'], reverse=True)
            
            return memorias[:limite]
            
        except Exception as e:
            print(f"❌ Erro ao buscar memórias relacionadas: {e}")
            return []
