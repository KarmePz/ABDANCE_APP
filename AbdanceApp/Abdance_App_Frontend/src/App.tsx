
import './App.css'
import {Background, Logo} from './components'
import { useDocumentTitle } from './hooks/useDocumentTitle';
import { useFavicon } from './hooks/useFavicon';

function App() {

  useDocumentTitle("Academia ABDANCE");
  useFavicon("/dance.ico")
  return (
    <>
      <Background />
      <Logo />
    </>
  )
}

export default App
