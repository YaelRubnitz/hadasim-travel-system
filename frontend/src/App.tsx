import { useState } from 'react';
import LoginPage from './pages/LoginPage';
import Dashboard from './pages/Dashboard';

function App() {
  const [teacher, setTeacher] = useState(null); // המורה המחוברת

  return (
    <div className="App">
      {!teacher ? (
        <LoginPage onLoginSuccess={(data) => setTeacher(data)} />
      ) : (
        <Dashboard teacher={teacher} onLogout={() => setTeacher(null)} />
      )}
    </div>
  );
}

export default App;