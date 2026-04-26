import { useState } from 'react'; 
import api from '../api/axios'; 
import { useNavigate } from 'react-router-dom'; 
import { useAuth } from '../context/AuthContext';

const LoginPage = () => {
    const [idNumber, setIdNumber] = useState('');
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const response = await api.post(`/auth/login?id_number=${idNumber}`);
            console.log("הצלחת!", response.data);
        } catch (err) {
            setError("מספר זהות לא תקין או מורה לא קיימת");
        }
    };

    return (
        <div style={{ padding: '20px', textAlign: 'center' }}>
            <h1>כניסת מורה</h1>
            <form onSubmit={handleSubmit}>
                {/* 3. שדה קלט (Input) */}
                <input 
                    type="text" 
                    placeholder="הזיני תעודת זהות" 
                    value={idNumber} 
                    onChange={(e) => setIdNumber(e.target.value)} 
                />
                <button type="submit">התחברי</button>
            </form>
            
            {/* 4. הצגת שגיאה אם יש */}
            {error && <p style={{ color: 'red' }}>{error}</p>}
        </div>
    );
};

export default LoginPage;