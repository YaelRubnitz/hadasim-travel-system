import { useState } from 'react';
import api from '../api/axios';

const LoginPage = ({ onLoginSuccess }) => {
    const [idNumber, setIdNumber] = useState('');
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        try {
            const response = await api.post(`/auth/login?teacher_id_input=${idNumber}`);            
            onLoginSuccess(response.data);
        } catch (err) {
            setError("מספר זהות לא תקין או מורה לא קיימת");
        }
    };

    return (
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh', background: '#f0f2f5', direction: 'rtl', fontFamily: 'Arial, sans-serif' }}>
            <div style={{ width: '100%', maxWidth: '400px', background: '#ffffff', padding: '40px', borderRadius: '12px', boxShadow: '0 8px 24px rgba(0,0,0,0.1)', textAlign: 'center' }}>
                <div style={{ marginBottom: '30px' }}>
                    <h1 style={{ fontSize: '24px', color: '#333', margin: '0 0 8px 0', fontWeight: 'bold' }}>מערכת טיולים </h1>
                    <p style={{ fontSize: '16px', color: '#666', margin: 0 }}>כניסת מורים </p>
                </div>

                <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                    <div style={{ textAlign: 'right' }}>
                        <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', fontWeight: '600', color: '#444' }}>תעודת זהות</label>
                        <input 
                            type="text" 
                            placeholder='הזיני ת"ז' 
                            value={idNumber} 
                            onChange={(e) => setIdNumber(e.target.value)} 
                            style={{ width: '100%', padding: '12px', border: '1px solid #ddd', borderRadius: '8px', fontSize: '16px', boxSizing: 'border-box', outline: 'none', textAlign: 'right' }}
                            required
                        />
                    </div>

                    <button type="submit" style={{ width: '100%', padding: '14px', background: '#007bff', color: 'white', border: 'none', borderRadius: '8px', fontSize: '16px', fontWeight: 'bold', cursor: 'pointer', transition: 'background 0.3s ease' }}>
                        התחברי למערכת
                    </button>
                </form>

                {error && (
                    <div style={{ marginTop: '20px', padding: '12px', background: '#fff1f0', border: '1px solid #ffa39e', color: '#cf1322', borderRadius: '6px', fontSize: '14px' }}>
                        ⚠️ {error}
                    </div>
                )}

                <div style={{ marginTop: '30px', color: '#999', fontSize: '12px' }}>
                
                </div>
            </div>
        </div>
    );
};

export default LoginPage;