import {useState, useEffect} from 'react'

import './App.css'
import {
  img_pos_1,
  img_pos_2,
  img_pos_3,
  img_pos_4,
  img_pos_5,
  img_template_0,
  img_template_1,
  img_template_2
  } from './assets/cards/index.js'


// let img_player = './assets/cards/player_photos/undy.png';

let api_url = 'http://127.0.0.1:5000/'
const remote_server = true


if (remote_server){
  api_url = 'https://vraposo.pythonanywhere.com/'
}
  

// const player_images = import.meta.glob("./assets/cards/player_photos/*")


function get_player_img(img_name){

  let imageUrl = new URL(`./assets/cards/player_photos/${img_name}.png`, import.meta.url).href
  console.log(imageUrl)
  return imageUrl
}



const team_count = 3;


function idx2pos(idx){
  switch (idx) {
    case 1:
      return img_pos_1;
    case 2:
      return img_pos_2;
    case 3:
      return img_pos_3;
    case 4:
      return img_pos_4;
    case 5:
      return img_pos_5;
  }
}

function idx2template(idx){
  switch (idx) {
    case 0:
      return img_template_0;
  
    case 1:
      return img_template_1;

    case 2:
      return img_template_2;
  }
}
let team_names =["3º: Mamacos United", "1º: Macaco Não Mata Macaco", "2º: Teamanduá"];

function get_stat_color(stat){
  if(stat == 100){
    return 'rgba(200, 120, 0, 1)';
  }
  return 'rgba(255, 255, 255, 0.5)';
}

function compute_average(stats){
  
  const sorter = (a, b) => b - a;
  const descendingCopy = stats.slice().sort(sorter);
  const biggest = descendingCopy.splice(0, 4);
  
  const sum = biggest.reduce((a, b) => a + b, 0);
  const avg = Math.floor(sum/4)

  
  return avg.toString()

}

function generate_player_cards(n_players, team, big_team, team_stats){

  let pad = 0;
  let html = []
  
  if (big_team){
    n_players -= 5;
    pad = 5;
  }
  else{
    if (team_stats[team] !== undefined){
      n_players = 5;
    }
  }
  // self.all = np.array([self.supp, self.kda, self.farm, self.versat, self.fight, self.push])
  console.log(n_players)
  for (let i = 0; i < n_players; i++) {
    html.push(
    <div className={"parent"}>
      <img src={idx2pos(team_stats[team][i + pad].pos)} className={'pos_img'}/>
      <img src={idx2template(team)} className={'card_img'}/>  
        <p className={'player_avg'}>{compute_average(team_stats[team][i + pad].stats)}</p>
        <p className={'player_name'}>{team_stats[team][i + pad].name}</p>
        <p className={'player_stat'} style={{paddingRight: '30%', paddingTop: '86.1%', color: get_stat_color(team_stats[team][i + pad].stats[3])}}>{team_stats[team][i + pad].stats[3]}</p>
        <p className={'player_stat'} style={{paddingRight: '80%', paddingTop: '86.1%', color: get_stat_color(team_stats[team][i + pad].stats[0])}}>{team_stats[team][i + pad].stats[0]}</p>
      
      
        <p className={'player_stat'} style={{paddingRight: '30%', paddingTop: '96.6%', color: get_stat_color(team_stats[team][i + pad].stats[4])}}>{team_stats[team][i + pad].stats[4]}</p>
        <p className={'player_stat'} style={{paddingRight: '80%', paddingTop: '96.6%', color: get_stat_color(team_stats[team][i + pad].stats[1])}}>{team_stats[team][i + pad].stats[1]}</p>
      
      
        <p className={'player_stat'} style={{paddingRight: '30%', paddingTop: '108.2%', color: get_stat_color(team_stats[team][i + pad].stats[5])}}>{team_stats[team][i + pad].stats[5]}</p>
        <p className={'player_stat'} style={{paddingRight: '80%', paddingTop: '108.2%', color: get_stat_color(team_stats[team][i + pad].stats[2])}}>{team_stats[team][i + pad].stats[2]}</p>
      
      <img src={get_player_img(team_stats[team][i + pad].img)} className={'player_img'}/>
      
    </div>
    )
  }

  return html
}





function generate_rows(idx_team, team_stats){
  let html = []

  let n_players = 0;

  if (team_stats[idx_team] !== undefined){
    console.log(team_stats);
    n_players = team_stats[idx_team].length;
  }

   

  html.push(
    <div className={"column"}>
      {generate_player_cards(n_players, idx_team, false, team_stats)}
    </div>
  )

  if (n_players > 5){
    html.push(
      <div className={"column"}>
        {generate_player_cards(n_players, idx_team, true, team_stats)}
      </div>
    )
  }

  return html
}

const display_order = [1, 2, 0];

function generate_teams(team_stats){
  
  let html_string = [];

  for (let i = 0; i < team_count; i++) {
    const j = display_order[i];
    html_string .push(
      <div className={'box-container-team'}>
        <h2>{team_names[j]}</h2>
        {generate_rows(j, team_stats)}     
      </div>
    )
  }

  return html_string
}


function App() {


  // const team_stats = get_team_stats();

  const [isLoading, setLoading] = useState(true);
  const [team_stats, set_team_stats] = useState();

  useEffect(() => {

    let promises = [];

    for (let i = 0; i < team_count; i++) {
      let url = api_url + "get_team_stats?team=" + i.toString();

      promises.push(fetch(url).then(function(response) {
        return response.json();
      }).then(function(data) {
        return data;
      }).catch(function(err) {
        console.log('Fetch Error :-S', err);
      }));

      Promise.all(promises).then((data) => {
        set_team_stats(data);
        setLoading(false);
      });

    }
    
  },[]);

  if (isLoading) {
    return <h2>Carregando...</h2>;
  }

  return (
    <>
      <div className={'box-container-header'}>
        <h1>Cartas de Jogadores RDC 3ª Edição</h1>
      </div>
      <div className={'box-container'}>
      {generate_teams(team_stats)}
      </div>
    </>
  )

}

export default App


