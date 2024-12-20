import { Routes, Route, Navigate } from 'react-router-dom';
import './App.css'
import SignInPage from './pages/SignIn/SignInPage';
import RegistrationPage from './pages/Registration/RegistrationPage';

const App: React.FC = () => {

  return (
    <Routes>
      <Route path='/signin' element={<SignInPage />} />
      <Route path='/registration' element={<RegistrationPage />} />
    </Routes>
  )
}

export default App
