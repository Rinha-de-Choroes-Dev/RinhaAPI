import { useState } from 'react'
import './App.css'
import card_template from './assets/cards/template.svg';

let player_count = 6
let card_width = (100/player_count).toString() + '%'
let team_name = "Mamacos United"

function App() {
  const [count, setCount] = useState(0)

  return (
    <>
      <div className={'box-container-header'}>
        <h1>Cartas de Jogadores RDC 3ª Edição</h1>
      </div>
      <div className={'box-container'}>
        <div className={'box-container-team'}>
            <div className={"column"}>
              <h2>{team_name}</h2>
              <img src={card_template} className={'card_img'} width={card_width}/>
              <img src={card_template} className={'card_img'} width={card_width}/>
              <img src={card_template} className={'card_img'} width={card_width}/>
              <img src={card_template} className={'card_img'} width={card_width}/>
              <img src={card_template} className={'card_img'} width={card_width}/>
              <img src={card_template} className={'card_img'} width={card_width}/>
            </div>
          </div>
          <div className={'box-container-team'}>
            <div className={"column"}>
              <h2>{team_name}</h2>
              <img src={card_template} className={'card_img'} width={card_width}/>
              <img src={card_template} className={'card_img'} width={card_width}/>
              <img src={card_template} className={'card_img'} width={card_width}/>
              <img src={card_template} className={'card_img'} width={card_width}/>
              <img src={card_template} className={'card_img'} width={card_width}/>
              <img src={card_template} className={'card_img'} width={card_width}/>
            </div>
          </div>
          <div className={'box-container-team'}>
            <div className={"column"}>
              <h2>{team_name}</h2>
              <img src={card_template} className={'card_img'} width={card_width}/>
              <img src={card_template} className={'card_img'} width={card_width}/>
              <img src={card_template} className={'card_img'} width={card_width}/>
              <img src={card_template} className={'card_img'} width={card_width}/>
              <img src={card_template} className={'card_img'} width={card_width}/>
              <img src={card_template} className={'card_img'} width={card_width}/>
            </div>
          </div>
      </div>
    </>
  )

  // return (
  //   <>
  //     <div>
  //       <a href="https://vitejs.dev" target="_blank">
  //         <img src={viteLogo} className="logo" alt="Vite logo" />
  //       </a>
  //       <a href="https://react.dev" target="_blank">
  //         <img src={reactLogo} className="logo react" alt="React logo" />
  //       </a>
  //     </div>
  //     <h1>Vite + React</h1>
  //     <div className="card">
  //       <button onClick={() => setCount((count) => count + 1)}>
  //         count is {count}
  //       </button>
  //       <p>
  //         Edit <code>src/App.jsx</code> and save to test HMR
  //       </p>
  //     </div>
  //     <p className="read-the-docs">
  //       Click on the Vite and React logos to learn more
  //     </p>
  //   </>
  // )
}

export default App


