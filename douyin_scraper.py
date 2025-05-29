import os
import json
import datetime
import requests
import bs4 as bs
import numpy as np
import pandas as pd
import urllib.request
from IPython.core.display import HTML

# ====== CONFIGURATION - CHANGEZ ICI VOTRE NICHE ======
NICHE = '美食'  # Changez simplement ce mot pour une autre niche
# Exemples : '美妆' (beauté), '旅行' (voyage), '时尚' (mode), '舞蹈' (danse), etc.
# =====================================================

def generate_path(path):
    folder = os.path.exists(path)
    if not folder:
        os.makedirs(path)

def video(video_url, file_name):
    return urllib.request.urlretrieve(video_url, file_name)

def cover(cover_url, file_name):
    return urllib.request.urlretrieve(cover_url, file_name)

def time(timestamp):
    return str(datetime.datetime.fromtimestamp(timestamp))

def is_within_24h(timestamp):
    """Vérifie si le timestamp est dans les dernières 24h"""
    now = datetime.datetime.now().timestamp()
    return (now - timestamp) <= 86400  # 86400 secondes = 24 heures

def scraper(topic):
    generate_path('./' + topic)
    topic_api = 'https://aweme-hl.snssdk.com/aweme/v1/hot/search/video/list/?hotword='
    re = requests.get(topic_api + topic)
    soup = bs.BeautifulSoup(re.content, 'html.parser')
    data = json.loads(soup.text)
    data = data['aweme_list']
    
    # Filtrer les vidéos des dernières 24h
    filtered_data = []
    for info in data:
        if is_within_24h(info['create_time']):
            filtered_data.append(info)
    
    if not filtered_data:
        print(f"Aucune vidéo trouvée dans les dernières 24h pour la niche '{topic}'")
        return
    
    print(f"Trouvé {len(filtered_data)} vidéos des dernières 24h pour la niche '{topic}'")
    
    # Extraire les données des vidéos filtrées
    desc = [info['desc'] for info in filtered_data]
    time_stamp = [info['create_time'] for info in filtered_data]
    create_time = [time(info['create_time']) for info in filtered_data]
    nickname = [info['author']['nickname'] for info in filtered_data]
    verify = [info['author']['custom_verify'] for info in filtered_data]
    share_count = [info['statistics']['share_count'] for info in filtered_data]
    forward_count = [info['statistics']['forward_count'] for info in filtered_data]
    like_count = [info['statistics']['digg_count'] for info in filtered_data]
    comment_count = [info['statistics']['comment_count'] for info in filtered_data]
    download_count = [info['statistics']['download_count'] for info in filtered_data]
    cover_url = [info['video']['cover']['url_list'][0] for info in filtered_data]
    cover_visual = ['<img src="' + url + '" width="100" >' for url in cover_url]
    
    video_url = []
    for info in filtered_data:
        try:
            video_url.append([i for i in info['video']['download_addr']['url_list'] if 'default' in i][0])
        except:
            video_url.append(None)
    
    df = pd.DataFrame({
        'desc': desc, 
        'nickname': nickname, 
        'verify': verify, 
        'time_stamp': time_stamp,
        'create_time': create_time, 
        'share_count': share_count, 
        'forward_count': forward_count,
        'like_count': like_count, 
        'comment_count': comment_count,
        'download_count': download_count, 
        'video_url': video_url,
        'cover_visual': cover_visual
    })
    
    # Sauvegarder avec timestamp pour éviter les conflits
    current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    df.to_csv(f'./{topic}/{topic}_24h_{current_time}.csv', encoding='utf-8-sig', index=False)
    
    # Télécharger les vidéos
    success_count = 0
    for num in range(0, len(filtered_data)):
        try:
            if df['video_url'][num] is not None:
                video_filename = f'./{topic}/{df["time_stamp"][num]}_24h.mp4'
                video(df['video_url'][num], video_filename)
                success_count += 1
                print(f'✅ Vidéo #{num+1}/{len(filtered_data)} téléchargée: {df["time_stamp"][num]}')
            else:
                print(f'❌ Vidéo #{num+1}/{len(filtered_data)} sans URL valide: {df["time_stamp"][num]}')
        except Exception as e:
            print(f'❌ Échec vidéo #{num+1}/{len(filtered_data)}: {df["time_stamp"][num]} - Erreur: {str(e)}')
            continue
    
    print(f"\n📊 RÉSUMÉ pour la niche '{topic}':")
    print(f"   - Vidéos trouvées (24h): {len(filtered_data)}")
    print(f"   - Vidéos téléchargées: {success_count}")
    print(f"   - Taux de succès: {(success_count/len(filtered_data)*100):.1f}%")

# ====== EXEMPLES DE NICHES POPULAIRES ======
# '美食' - Nourriture/Cuisine
# '美妆' - Beauté/Maquillage  
# '旅行' - Voyage
# '时尚' - Mode/Fashion
# '舞蹈' - Danse
# '音乐' - Musique
# '运动' - Sport
# '搞笑' - Humour/Comédie
# '宠物' - Animaux domestiques
# '健身' - Fitness
# '游戏' - Jeux vidéo
# '科技' - Technologie
# '教育' - Éducation
# '艺术' - Art
# '做饭' - Cuisine (cooking)
# ==========================================

if __name__ == "__main__":
    print("🚀 Lancement du scraper Douyin - Dernières 24h")
    print(f"🎯 Niche sélectionnée: {NICHE}")
    print("-" * 50)
    
    scraper(NICHE)
    
    print("\n✨ Script terminé!")
    print(f"📁 Vérifiez le dossier './{NICHE}/' pour vos fichiers")
