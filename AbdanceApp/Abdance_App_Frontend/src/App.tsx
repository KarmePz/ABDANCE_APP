
import './App.css'
import {Background, Logo, InputButton, CustomForm} from './components'
import { useDocumentTitle } from './hooks/useDocumentTitle';
import { useFavicon } from './hooks/useFavicon';

function App() {

  useDocumentTitle("Academia ABDANCE");
  useFavicon("/dance.ico")
  return (
    <>
      <Background />
      <Logo />
      <InputButton name="Input test"  placeholder='Ingrese su contraseña'/>
      <CustomForm></CustomForm>
    </>
  )
}

export default App
