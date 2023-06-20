## Análise de Estatísticas para as Cartinhas da Rinha de Chorões

[Rinha de Chorões](https://www.twitch.tv/rinhadechoroes) é um campeonato amador de Dota 2 e para sua terceira edição foi desenvolvida 
uma página web contendo "cartas de Jogadores" como esta:

<p align="center">
<img src=https://i.imgur.com/SClKzTj.png/>
 </p>

Devido a limitações na organização do campeonato, apenas a fase de grupos está disponível para que informações sejam extraídas. Além disso
como esse projeto se trata de um protótipo, apenas os três primeiros colocados tiveram suas cartas geradas. O resultado encontra-se
disponível em: https://vravaglia.github.io/RinhaAPI/

Neste repositório está contido o código tanto do backend, desenvolvido em [Flask](https://flask.palletsprojects.com/en/2.3.x/), quanto do
frontend, desenvolvido com [React](https://react.dev/) e [Vite](https://vitejs.dev/).

### Fonte dos dados

Os números mostrados nas cartinhas são obtidos a partir de manipulações nas estatísticas dos jogadores. Essas estatísticas
são as métricas de desempenho disponibilizadas no final de cada jogo, como ouro por minuto ou abates. Para todos os jogadores
a fonte dessas estatísticas são os próprios jogos da Rinha. Ou seja, apenas o desepenho obtido pelos jogadores durante o
campeonato é analisado. Consequentemente, é necessário obter as estatísitcas das partidas do campeonato para cada jogador.
   
No inicio do campeonato a organização conseguiu em conjunto com a Valve oficializar o campeonato. Isso permitiu que todas 
as partidas realizadas até a data do término do ticket sejam publicas. Por conta disso, todas as partidas realizadas
nesse período estão disponíveis em sites como Opendota, Stratz e Dotabuff. As partidas com ticket tem seus dados 
extraídos da seguite forma:

A duração das partidas é extraída do próprio site do [Dotabuff](dotabuuff.com) com [Selenium](https://www.selenium.dev/).
As demais estatísticas são obtidas com a [API do Opendota](https://docs.opendota.com/).
    
### Significado dos dados presentes nas cartinhas

Cada cartinha atualmente detém os seguintes atributos e calculados (em teoria) como se segue, antes de serem normalizados. O valor no canto superior esquerdo é a média
das 4 maiores estatísticas do jogador.

* SUP ("Suporte"):
    
    $Media((\frac{CuraRealizada}{2000} + Wards + Sentries)/Duracao)$
    
    onde "Duracao" é a duração da partida em minutos.
    
* KDA:
    
    $Media((Abates + Assistencias)/(Mortes + 1))$
    
* FRM ("Farm"):
    
    $Media(LastHits)$

* VER ("Versatilidade"):
    
    $\frac{NumeroDeHeroisUnicos}{NumeroDePartidas}$

* FGT ("Fight"):
    
    $Media((Abates + Assistencias + \frac{DanoEmHerois}{2000})/Duracao)$
    
* PSH ("Push"):
    
    $Media(DanoEmTorres)$
    
Depois que as estatísticas de cada jogador é calculada, todas elas são normalizadas quanto ao valor de uma dada estatística quando comparada com os outros jogadores. Por exemplo, digamos que tenhamos dois jogadores, o primeiro com SUP = 45, e o segundo com SUP = 132. Para normalizar fazemos:

$SUP_1 = 100\times\frac{45}{132} = 34$

$SUP_2 = 100\times\frac{132}{132} = 100$
