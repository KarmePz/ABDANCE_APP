
import './App.css'
import {Background, Logo, LoginForm} from './components'
import { useDocumentTitle } from './hooks/useDocumentTitle';
import { useFavicon } from './hooks/useFavicon';

function App() {

  useDocumentTitle("Academia ABDANCE");
  useFavicon("/dance.ico")
  return (
    <>
    
      <Background />
      <Logo />
      <LoginForm ></LoginForm>


      <h3 className='relative top-40'> ¿Te interesa saber sobre nuestros eventos? <a href='https://www.youtube.com' target='blank'>¡Hace click Aqui!</a></h3>
    
    </>
  )
}

export default App
