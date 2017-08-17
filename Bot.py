# -*- coding: utf-8 -*-

import requests
import json
import telegram
from pprint import pprint
import telepot
import telepot.helper
from telepot.loop import MessageLoop
import time
import sys
from telepot.delegate import (
    per_chat_id, create_open, pave_event_space, include_callback_query_chat_id)


reload(sys)
sys.setdefaultencoding("utf-8")


TOKEN = '427110287:AAF7RhD-SKhyKuDrgtXsKeJrilngVmBdw-4'
Times_slug = range(1,25)
Times_nomes = range(1,25)
Times_pontuacao = range(1,25)
#Atleta_id = range(1,13)
#Atleta_nome = range(1,13)

class Cartola(object):
    """docstring for Cartola"""
    def __init__(self, email=None, password=None, attempts=1):
        
        self._api_url = 'https://api.cartolafc.globo.com'
        self._auth_url = 'https://login.globo.com/api/authentication'
        self._email = email
        self._password = password
        self._glb_id = None
        self.attempts = attempts if isinstance(attempts, int) and attempts > 0 else 1

        if bool(email) != bool(password):
            raise CartolaFCError('E-mail ou senha ausente')
        elif all((email, password)):
            self.set_credentials(email, password)

    def set_credentials(self, email, password):  

        self._email = email
        self._password = password
        response = requests.post(self._auth_url,json=dict(payload=dict(email=self._email, password=self._password, serviceId=4728)))
        body = response.json()
        if response.status_code == 200:
            self._glb_id = body['glbId']
            print(self._glb_id)
        else:
            raise CartolaFCError(body['userMessage'])
    def liga(self):
        url='{api_url}/auth/liga/os-mitos-da-vli'.format(api_url=self._api_url)
        headers = {'X-GLB-Token': self._glb_id} if self._glb_id else None
        data = requests.get(url, headers=headers)
        return json.loads(data.content)
    def time(self, slug):
        param = 'slug'
        value = slug
        url='{api_url}/time/{param}/{value}'.format(api_url=self._api_url, param=param, value=value)
        headers = {'X-GLB-Token': self._glb_id} if self._glb_id else None
        data = requests.get(url)
        return json.loads(data.content)
    def parciais(self):
        url='{api_url}/atletas/pontuados'.format(api_url=self._api_url)
        headers = {'X-GLB-Token': self._glb_id} if self._glb_id else None
        data = requests.get(url, headers=headers)
        return json.loads(data.content)
    def parcial_time(self, slug, parciais):
        
        Atleta_id = range(1,14)
        Atleta_nome = range(1,16)
        Atleta_nome[14] = 'Total' 
        Time_pontuacao = range(1,16)
        Time_pontuacao[14] = 0 

        atletas = self.time(slug)

        i=1
        for atleta in atletas['atletas']:
            Atleta_nome[i]=atleta['apelido']
            Atleta_id[i]=atleta['atleta_id']
            i=i+1
        #parciais = self.parciais();
        #pprint (parciais)
        i=1
        for i in range(1,13):
            #k=parciais['atletas'][str(Atleta_id[i])]['pontuacao']
            #print(k)
            try:
                #print (Atleta_id[i])
                k=parciais['atletas'][str(Atleta_id[i])]['pontuacao']
            except KeyError, e:
                k=0
            
            #print (k)
            Time_pontuacao[i] = k                      
            Time_pontuacao[14]=Time_pontuacao[14]+Time_pontuacao[i]

        return(Atleta_nome, Time_pontuacao)
    def mercado(self):
        url='{api_url}/mercado/status'.format(api_url=self._api_url)
        headers = {'X-GLB-Token': self._glb_id} if self._glb_id else None
        data = requests.get(url, headers=headers)
        a=json.loads(data.content)
        #pprint(a)
        b=' '
        if a['status_mercado'] == 1:
            b = 'Mercado Aberto' 
        if a['status_mercado'] == 2:
            b= 'Mercado Fechado'
        if a['status_mercado'] == 3:
            b= 'Mercado em atualização'
        if a['status_mercado'] == 4:
            b= 'Mercado em Manuteção'
        if a['status_mercado'] == 6:
            b= 'Final de temporada'

        return (b)


def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    if content_type == 'text':
        if msg['text'] == 'Parcial':
            bot.sendMessage(chat_id, 'ola!!!')
            c=a.liga()
            d=a.mercado()
            #print(d,'opa')

            if d == 'Mercado Fechado':
            

                i=1
                for time in c['times']:
                    #print (time['slug'])
                    Times_slug[i]=time['slug']
                    Times_nomes[i]=time['nome']
                    i=i+1 

                i=1
                for i in range(1,21):
                    parciais = a.parciais()
                    jogador, pontos = a.parcial_time(Times_slug[i], parciais)
                    bot.sendMessage(chat_id, Times_nomes[i])
                    #print (Times_nomes[i])
                    Menssagem = '{jogador}  {pontos}'.format(jogador=jogador[14], pontos=str(pontos[14]))
                    Menssagem1 = None
                    bot.sendMessage(chat_id, Menssagem)
                    #print jogador[14],'        ',pontos[14]
                    k=1
                    for k in range (1, 13):
                        Menssagem1 = '{menssagem} \n {jogador}  {pontos}'.format(menssagem=Menssagem1, jogador=jogador[k], pontos=str(pontos[k]))
                        #print jogador[k], '        ', pontos[k]
                    bot.sendMessage(chat_id, Menssagem1)
                
            else:
                print(d)

                bot.sendMessage(chat_id, d)

        else:
            
            c=a.liga()
            d=a.mercado()
            #pprint (c)
            time_slug = None

            if d == 'Mercado Fechado':
                for time in c['times']:
                    if msg['text'] == time['nome']:
                        time_slug = time['slug']
                    
                        

#                    time_slug = c['times'][msg['text']]['slug']
 #                   pprint (time_slug)
                if time_slug:

                    parciais=a.parciais()
                    jogador, pontos = a.parcial_time(time_slug, parciais)
                    Menssagem = '{jogador}  {pontos}'.format(jogador=jogador[14], pontos=str(pontos[14]))
                    Menssagem1 = None
                    bot.sendMessage(chat_id, Menssagem)
                    k=1
                    for k in range (1, 13):
                        Menssagem1 = '{menssagem} \n {jogador}  {pontos}'.format(menssagem=Menssagem1, jogador=jogador[k], pontos=str(pontos[k]))
                        #print jogador[k], '        ', pontos[k]
                    bot.sendMessage(chat_id, Menssagem1)
                else:
                    bot.sendMessage(chat_id, 'Time não esta na liga')


            else:
                #print(d)
                bot.sendMessage(chat_id, d)
           
            bot.sendMessage(chat_id, 'Me mande apenas "Parcial" que enviarei resultado de todos os times')

a=Cartola(email='jrafante89@gmail.com',password='wdoi8912')



bot=telepot.Bot(TOKEN)
bot.getUpdates(offset=100000001)
MessageLoop(bot, handle).run_as_thread()


while 1:
    time.sleep(10)








    


#a=Cartola(email='jrafante89@gmail.com',password='wdoi8912')
#a.set_credentials('jrafante89@gmail.com','wdoi8912')
#b=a.liga()
#print(b.content)
#c=json.loads(b.content)
#pprint (b.content)
#pprint(c.get('times','nome'))
#i=1
#for time in c['times']:
#    print (time['slug'])
#    Times_slug[i]=time['slug']
#    Times_nomes[i]=time['nome']
#    i=i+1 
#d=a.time(Times_slug[1])
#i=1
#for i in range(1,21):
#    jogador, pontos = a.parcial_time(Times_slug[i])
#    print (Times_nomes[i])
#    print jogador[14],'        ',pontos[14]
#    k=1
#    for k in range (1, 12):
#        print jogador[k], '        ', pontos[k]


#e=a.parcial_atletas(Atleta_id)
#f=e['atletas']['37281']['pontuacao']
#print(type(f))
#pprint(d['atletas'])
#pprint (e['atletas']['37281']['pontuacao'])
#print (b.content['times'])

