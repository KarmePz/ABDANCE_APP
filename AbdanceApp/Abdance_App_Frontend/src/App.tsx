
import { Link } from 'react-router-dom';
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
        <div className="min-h-screen flex flex-col items-center justify-center px-4">
          <LoginForm ></LoginForm>


          <h3 className="mt-10 text-center text-white"> ¿Te interesa saber sobre nuestros eventos? <Link to="/eventos"  target='blank'>¡Hace click Aqui!</Link></h3>
        </div>
    </>
  )
}

export default App
