import discord
from discord.ext import commands
import random
import json
import os
from config import TOKEN

# Configuration du bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Fichier pour sauvegarder les scores
SCORES_FILE = 'scores.json'

# Charger les scores depuis le fichier
def load_scores():
    if os.path.exists(SCORES_FILE):
        with open(SCORES_FILE, 'r') as f:
            return json.load(f)
    return {}

# Sauvegarder les scores dans le fichier
def save_scores(scores):
    with open(SCORES_FILE, 'w') as f:
        json.dump(scores, f, indent=2)

# Initialiser les scores
scores = load_scores()

@bot.event
async def on_ready():
    print(f'{bot.user} est connecté!')
    print(f'Bot ID: {bot.user.id}')

@bot.command(name='ppc', aliases=['pierre', 'papier', 'ciseaux'])
async def pierre_papier_ciseaux(ctx, choix_joueur=None):
    """
    Joue à pierre-papier-ciseaux contre le bot
    Usage: !ppc pierre/papier/ciseaux
    """
    
    # Vérifier si le joueur a fait un choix valide
    choix_valides = ['pierre', 'papier', 'ciseaux', '🗿', '📄', '✂️']
    
    if choix_joueur is None:
        embed = discord.Embed(
            title="🎮 Pierre-Papier-Ciseaux",
            description="Utilise `!ppc pierre`, `!ppc papier` ou `!ppc ciseaux`\n"
                       "Tu peux aussi utiliser les emojis: 🗿 📄 ✂️",
            color=0x3498db
        )
        await ctx.send(embed=embed)
        return
    
    choix_joueur = choix_joueur.lower()
    
    # Convertir les emojis en mots
    emoji_to_word = {'🗿': 'pierre', '📄': 'papier', '✂️': 'ciseaux'}
    if choix_joueur in emoji_to_word:
        choix_joueur = emoji_to_word[choix_joueur]
    
    if choix_joueur not in ['pierre', 'papier', 'ciseaux']:
        await ctx.send("❌ Choix invalide! Utilise `pierre`, `papier` ou `ciseaux`")
        return
    
    # Choix du bot
    choix_bot = random.choice(['pierre', 'papier', 'ciseaux'])
    
    # Déterminer le gagnant
    def determiner_gagnant(joueur, bot):
        if joueur == bot:
            return "égalité"
        elif (joueur == "pierre" and bot == "ciseaux") or \
             (joueur == "papier" and bot == "pierre") or \
             (joueur == "ciseaux" and bot == "papier"):
            return "joueur"
        else:
            return "bot"
    
    resultat = determiner_gagnant(choix_joueur, choix_bot)
    
    # Emojis pour les choix
    emojis = {'pierre': '🗿', 'papier': '📄', 'ciseaux': '✂️'}
    
    # Mise à jour des scores
    user_id = str(ctx.author.id)
    if user_id not in scores:
        scores[user_id] = {'victoires': 0, 'défaites': 0, 'égalités': 0, 'nom': ctx.author.display_name}
    
    # Créer l'embed de résultat
    embed = discord.Embed(title="🎮 Pierre-Papier-Ciseaux", color=0x3498db)
    embed.add_field(name="Ton choix", value=f"{emojis[choix_joueur]} {choix_joueur.capitalize()}", inline=True)
    embed.add_field(name="Mon choix", value=f"{emojis[choix_bot]} {choix_bot.capitalize()}", inline=True)
    embed.add_field(name="‎", value="‎", inline=True)  # Espace pour la mise en forme
    
    if resultat == "égalité":
        embed.add_field(name="Résultat", value="🤝 Égalité!", inline=False)
        embed.color = 0xf39c12
        scores[user_id]['égalités'] += 1
    elif resultat == "joueur":
        embed.add_field(name="Résultat", value="🎉 Tu as gagné!", inline=False)
        embed.color = 0x2ecc71
        scores[user_id]['victoires'] += 1
    else:
        embed.add_field(name="Résultat", value="😅 J'ai gagné!", inline=False)
        embed.color = 0xe74c3c
        scores[user_id]['défaites'] += 1
    
    # Ajouter les statistiques
    stats = scores[user_id]
    total_parties = stats['victoires'] + stats['défaites'] + stats['égalités']
    embed.add_field(
        name="📊 Tes statistiques",
        value=f"Victoires: {stats['victoires']}\n"
              f"Défaites: {stats['défaites']}\n"
              f"Égalités: {stats['égalités']}\n"
              f"Total: {total_parties} parties",
        inline=False
    )
    
    embed.set_footer(text=f"Demandé par {ctx.author.display_name}")
    
    await ctx.send(embed=embed)
    
    # Sauvegarder les scores
    save_scores(scores)

@bot.command(name='stats')
async def statistiques(ctx, user: discord.Member = None):
    """
    Affiche les statistiques de pierre-papier-ciseaux
    Usage: !stats [@utilisateur]
    """
    
    if user is None:
        user = ctx.author
    
    user_id = str(user.id)
    
    if user_id not in scores:
        await ctx.send(f"❌ {user.display_name} n'a encore joué aucune partie!")
        return
    
    stats = scores[user_id]
    total = stats['victoires'] + stats['défaites'] + stats['égalités']
    
    if total == 0:
        await ctx.send(f"❌ {user.display_name} n'a encore joué aucune partie!")
        return
    
    # Calculer le pourcentage de victoires
    pourcentage_victoires = (stats['victoires'] / total * 100) if total > 0 else 0
    
    embed = discord.Embed(
        title=f"📊 Statistiques de {user.display_name}",
        color=0x9b59b6
    )
    
    embed.add_field(name="🏆 Victoires", value=stats['victoires'], inline=True)
    embed.add_field(name="💀 Défaites", value=stats['défaites'], inline=True)
    embed.add_field(name="🤝 Égalités", value=stats['égalités'], inline=True)
    embed.add_field(name="🎮 Total parties", value=total, inline=True)
    embed.add_field(name="📈 Taux de victoire", value=f"{pourcentage_victoires:.1f}%", inline=True)
    
    # Ajouter un rang basé sur le taux de victoire
    if pourcentage_victoires >= 60:
        rang = "🥇 Champion"
    elif pourcentage_victoires >= 45:
        rang = "🥈 Expert"
    elif pourcentage_victoires >= 30:
        rang = "🥉 Joueur"
    else:
        rang = "🔰 Débutant"
    
    embed.add_field(name="🏅 Rang", value=rang, inline=True)
    embed.set_thumbnail(url=user.display_avatar.url)
    
    await ctx.send(embed=embed)

@bot.command(name='classement', aliases=['top', 'leaderboard'])
async def classement(ctx):
    """
    Affiche le classement des meilleurs joueurs
    """
    
    if not scores:
        await ctx.send("❌ Aucune statistique disponible!")
        return
    
    # Trier les joueurs par nombre de victoires
    joueurs_tries = []
    for user_id, stats in scores.items():
        total = stats['victoires'] + stats['défaites'] + stats['égalités']
        if total > 0:  # Seulement les joueurs qui ont joué
            pourcentage = (stats['victoires'] / total * 100)
            joueurs_tries.append({
                'nom': stats['nom'],
                'victoires': stats['victoires'],
                'total': total,
                'pourcentage': pourcentage
            })
    
    # Trier par nombre de victoires puis par pourcentage
    joueurs_tries.sort(key=lambda x: (x['victoires'], x['pourcentage']), reverse=True)
    
    embed = discord.Embed(
        title="🏆 Classement Pierre-Papier-Ciseaux",
        color=0xf1c40f
    )
    
    medailles = ["🥇", "🥈", "🥉"]
    
    for i, joueur in enumerate(joueurs_tries[:10]):  # Top 10
        medaille = medailles[i] if i < 3 else f"{i+1}."
        embed.add_field(
            name=f"{medaille} {joueur['nom']}",
            value=f"🏆 {joueur['victoires']} victoires sur {joueur['total']} parties ({joueur['pourcentage']:.1f}%)",
            inline=False
        )
    
    await ctx.send(embed=embed)

@bot.command(name='reset')
async def reset_stats(ctx):
    """
    Remet à zéro tes statistiques
    """
    user_id = str(ctx.author.id)
    
    if user_id not in scores:
        await ctx.send("❌ Tu n'as pas de statistiques à réinitialiser!")
        return
    
    # Demander confirmation
    embed = discord.Embed(
        title="⚠️ Confirmation",
        description="Es-tu sûr de vouloir remettre à zéro tes statistiques?\n"
                   "Cette action est irréversible!",
        color=0xe74c3c
    )
    
    message = await ctx.send(embed=embed)
    await message.add_reaction("✅")
    await message.add_reaction("❌")
    
    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in ["✅", "❌"] and reaction.message.id == message.id
    
    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=check)
        
        if str(reaction.emoji) == "✅":
            del scores[user_id]
            save_scores(scores)
            await ctx.send("✅ Tes statistiques ont été réinitialisées!")
        else:
            await ctx.send("❌ Réinitialisation annulée.")
            
    except:
        await ctx.send("⏰ Temps écoulé, réinitialisation annulée.")

# Commande d'aide personnalisée
@bot.command(name='aide', aliases=['help_ppc'])
async def aide(ctx):
    """
    Affiche l'aide du bot pierre-papier-ciseaux
    """
    embed = discord.Embed(
        title="🎮 Bot Pierre-Papier-Ciseaux",
        description="Voici toutes les commandes disponibles:",
        color=0x3498db
    )
    
    commandes = [
        ("!ppc <choix>", "Joue une partie (pierre/papier/ciseaux ou 🗿📄✂️)"),
        ("!stats [@utilisateur]", "Affiche les statistiques"),
        ("!classement", "Affiche le top des joueurs"),
        ("!reset", "Remet à zéro tes statistiques"),
        ("!aide", "Affiche cette aide")
    ]
    
    for commande, description in commandes:
        embed.add_field(name=commande, value=description, inline=False)
    
    embed.set_footer(text="Amusez-vous bien! 🎉")
    
    await ctx.send(embed=embed)

# Gestionnaire d'erreurs
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return  # Ignorer les commandes inexistantes
    
    embed = discord.Embed(
        title="❌ Erreur",
        description=f"Une erreur s'est produite: {str(error)}",
        color=0xe74c3c
    )
    await ctx.send(embed=embed)

# Remplace 'TON_TOKEN_BOT' par le vrai token de ton bot
if __name__ == "__main__":
    bot.run(TOKEN)
