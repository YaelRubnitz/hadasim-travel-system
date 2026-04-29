import { useState, useEffect } from 'react';
import api from '../api/axios';
import MapComponent from '../components/MapComponent';

const Dashboard = ({ teacher, onLogout }) => {
    const [view, setView] = useState('manage'); 
    const [myStudents, setMyStudents] = useState([]);
    const [allTeachers, setAllTeachers] = useState([]);
    const [allStudents, setAllStudents] = useState([]);
    const [farStudents, setFarStudents] = useState([]);
    
    const [showMyStudents, setShowMyStudents] = useState(true);
    const [showAllTeachers, setShowAllTeachers] = useState(false);
    const [showAllStudents, setShowAllStudents] = useState(false);
    const [showFarPanel, setShowFarPanel] = useState(false);
    
    const [message, setMessage] = useState({ text: '', type: '' });
    const [searchTz, setSearchTz] = useState('');
    const [singleResult, setSingleResult] = useState(null);

    const [newStudent, setNewStudent] = useState({ tz: '', first_name: '', last_name: '' });
    const [newTeacher, setNewTeacher] = useState({ tz: '', first_name: '', last_name: '', class_name: '' });

    const showFeedback = (text, type = 'success') => {
        setMessage({ text, type });
        setTimeout(() => setMessage({ text: '', type: '' }), 3000);
    };

    const fetchCoreData = async () => {
        try {
            // קריאה לכל הנתונים במקביל
            const [myClassRes, allTeachersRes, allStudentsRes, locationsRes, farRes] = await Promise.all([
                api.get('/students/my-class'),
                api.get('/teachers/'),
                api.get('/students/'),
                api.get('/locations/class-last-locations'),
                api.get('/locations/far-students')
            ]);
            
            const studentsWithLoc = myClassRes.data.map(s => {
                const loc = locationsRes.data.find(l => l.student_tz?.toString() === s.tz?.toString());
                return loc ? { ...s, latitude: loc.latitude, longitude: loc.longitude } : s;
            });
            
            setMyStudents(studentsWithLoc);
            setAllTeachers(allTeachersRes.data);
            setAllStudents(allStudentsRes.data);
            setFarStudents(farRes.data);

            // אם יש תלמידות רחוקות והמורה במצב מפה - נפתח את הפאנל אוטומטית כהתראה
            if (farRes.data.length > 0 && view === 'map') {
                setShowFarPanel(true);
            }
        } catch (err) {
            console.error("Data fetch failed", err);
        }
    };

    // רענון אוטומטי כל דקה
    useEffect(() => {
        fetchCoreData(); 
        const ticker = setInterval(fetchCoreData, 60000); 
        return () => clearInterval(ticker);
    }, [view]); // המערכת תתרענן גם כשמחליפים מצב תצוגה

    const handleSearch = async () => {
        if (!searchTz) return;
        setSingleResult(null);
        try {
            const resS = await api.get(`/students/${searchTz}`);
            if (resS.data) {
                setSingleResult({ ...resS.data, type: 'תלמידה' });
                return;
            }
        } catch (e) {
            try {
                const resT = await api.get(`/teachers/${searchTz}`);
                if (resT.data) setSingleResult({ ...resT.data, type: 'מורה' });
            } catch (e2) {
                showFeedback("לא נמצאו נתונים עבור תעודת זהות זו", "error");
            }
        }
    };

    const handleAddStudent = async (e) => {
        e.preventDefault();
        try {
            await api.post('/students/', { ...newStudent, class_name: teacher.class_name });
            setNewStudent({ tz: '', first_name: '', last_name: '' });
            fetchCoreData();
            showFeedback("התלמידה נוספה בהצלחה!");
        } catch (err) {
            showFeedback("שגיאה בהוספת תלמידה", "error");
        }
    };

    const handleAddTeacher = async (e) => {
        e.preventDefault();
        try {
            await api.post('/teachers/', { ...newTeacher });
            setNewTeacher({ tz: '', first_name: '', last_name: '', class_name: '' });
            fetchCoreData();
            showFeedback("המורה נוספ/ה בהצלחה!");
        } catch (err) {
            showFeedback("שגיאה בהוספת מורה", "error");
        }
    };

    return (
        <div style={containerStyle}>
            {message.text && (
                <div style={{
                    ...feedbackStyle,
                    backgroundColor: message.type === 'success' ? '#d4edda' : '#f8d7da',
                    color: message.type === 'success' ? '#155724' : '#721c24',
                    border: `1px solid ${message.type === 'success' ? '#c3e6cb' : '#f5c6cb'}`
                }}>
                    {message.text}
                </div>
            )}

            <header style={headerStyle}>
                <div>
                    <h2 style={{ margin: 0 }}>שלום {teacher?.first_name}</h2>
                    <small>ניהול מערכת - כיתה {teacher?.class_name}</small>
                </div>
                <button onClick={onLogout} style={logoutBtnStyle}>יציאה</button>
            </header>

            <nav style={navStyle}>
                <button onClick={() => setView('manage')} style={{ ...navBtnStyle, background: view === 'manage' ? '#007bff' : '#f8f9fa', color: view === 'manage' ? 'white' : 'black' }}>📁 ניהול ורישום</button>
                <button onClick={() => setView('map')} style={{ ...navBtnStyle, background: view === 'map' ? '#007bff' : '#f8f9fa', color: view === 'map' ? 'white' : 'black' }}>📍 מפת טיול (Live)</button>
            </nav>

            {view === 'manage' ? (
                <div style={gridStyle}>
                    <section style={cardStyle}>
                        <h3 style={sectionTitleStyle}>רישום חדש</h3>
                        
                        <form onSubmit={handleAddStudent} style={{ marginBottom: '30px', paddingBottom: '20px', borderBottom: '2px solid #eee' }}>
                            <h4 style={{ marginBottom: '10px' }}>הוספת תלמידה חדשה</h4>
                            <input placeholder='ת"ז' style={inputStyle} value={newStudent.tz} onChange={e => setNewStudent({...newStudent, tz: e.target.value})} required />
                            <input placeholder="שם פרטי" style={inputStyle} value={newStudent.first_name} onChange={e => setNewStudent({...newStudent, first_name: e.target.value})} required />
                            <input placeholder="שם משפחה" style={inputStyle} value={newStudent.last_name} onChange={e => setNewStudent({...newStudent, last_name: e.target.value})} required />
                            <div style={{ position: 'relative' }}>
                                <label style={{ fontSize: '12px', color: '#666' }}>כיתה (אוטומטי):</label>
                                <input value={teacher?.class_name} readOnly style={{ ...inputStyle, background: '#e9ecef', cursor: 'not-allowed' }} />
                            </div>
                            <button type="submit" style={submitBtnStyle}>הוסף תלמידה</button>
                        </form>

                        <form onSubmit={handleAddTeacher}>
                            <h4 style={{ marginBottom: '10px' }}>הוספת מורה חדש/ה</h4>
                            <input placeholder='ת"ז' style={inputStyle} value={newTeacher.tz} onChange={e => setNewTeacher({...newTeacher, tz: e.target.value})} required />
                            <input placeholder="שם פרטי" style={inputStyle} value={newTeacher.first_name} onChange={e => setNewTeacher({...newTeacher, first_name: e.target.value})} required />
                            <input placeholder="שם משפחה" style={inputStyle} value={newTeacher.last_name} onChange={e => setNewTeacher({...newTeacher, last_name: e.target.value})} required />
                            <input placeholder="שם כיתה" style={inputStyle} value={newTeacher.class_name} onChange={e => setNewTeacher({...newTeacher, class_name: e.target.value})} required />
                            <button type="submit" style={{ ...submitBtnStyle, background: '#28a745' }}>הוסף מורה</button>
                        </form>
                    </section>

                    <section>
                        <h3 style={sectionTitleStyle}>חיפוש ומעקב</h3>
                        
                        <div style={{ display: 'flex', gap: '5px', marginBottom: '15px' }}>
                            <input 
                                placeholder='חפשי לפי ת"ז...' 
                                style={{ ...inputStyle, marginBottom: 0, flex: 1 }} 
                                value={searchTz} 
                                onChange={e => setSearchTz(e.target.value)} 
                            />
                            <button onClick={handleSearch} style={searchBtnStyle}>🔍</button>
                        </div>

                        {singleResult && (
                            <div style={resultCardStyle}>
                                <strong>נמצא/ה {singleResult.type}:</strong> {singleResult.first_name} {singleResult.last_name}  כיתה: {singleResult.class_name}
                                <button onClick={() => setSingleResult(null)} style={{ float: 'left', border: 'none', background: 'none', cursor: 'pointer' }}>✖</button>
                            </div>
                        )}

                        <div style={listContainerStyle}>
                            <button onClick={() => setShowMyStudents(!showMyStudents)} style={toggleBtnStyle}>
                                {showMyStudents ? '🔼 הסתר תלמידות שלי' : '🔽 הצג תלמידות שלי'}
                            </button>
                            {showMyStudents && (
                                <ul style={expandedListStyle}>
                                    {myStudents.map(s => <li key={s.tz} style={listItemStyle}><strong>{s.tz}</strong> - {s.first_name} {s.last_name}</li>)}
                                </ul>
                            )}

                            <button onClick={() => setShowAllTeachers(!showAllTeachers)} style={toggleBtnStyle}>
                                {showAllTeachers ? '🔼 הסתר את כל המורות' : '🔽 הצג את כל המורות'}
                            </button>
                            {showAllTeachers && (
                                <div style={expandedListStyle}>
                                    {allTeachers.map(t => <div key={t.tz} style={listItemStyle}>{t.tz} - {t.first_name} {t.last_name} <strong>({t.class_name})</strong></div>)}
                                </div>
                            )}

                            <button onClick={() => setShowAllStudents(!showAllStudents)} style={toggleBtnStyle}>
                                {showAllStudents ? '🔼 הסתר את כל התלמידות' : '🔽 הצג את כל התלמידות'}
                            </button>
                            {showAllStudents && (
                                <div style={expandedListStyle}>
                                    {allStudents.map(s => <div key={s.tz} style={listItemStyle}>{s.tz} - {s.first_name} {s.last_name} <strong>({s.class_name})</strong></div>)}
                                </div>
                            )}
                        </div>
                    </section>
                </div>
            ) : (
                /* --- תצוגת מפה ובונוס תלמידות רחוקות --- */
                <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                    <div style={mapWrapperStyle}>
                        <MapComponent students={myStudents} />
                    </div>

                    {/* פאנל התראות מרחק נפתח/נסגר */}
                    <section style={{ 
                        ...cardStyle, 
                        borderColor: farStudents.length > 0 ? '#dc3545' : '#eee', 
                        width: '100%',
                        transition: 'all 0.3s ease'
                    }}>
                        <button 
                            onClick={() => setShowFarPanel(!showFarPanel)} 
                            style={{ 
                                ...toggleBtnStyle, 
                                color: farStudents.length > 0 ? '#dc3545' : '#333',
                                backgroundColor: farStudents.length > 0 ? '#fff5f5' : '#f8f9fa'
                            }}
                        >
                            {showFarPanel ? '🔼 סגור רשימת חריגות מרחק' : `🔽 הצג תלמידות מחוץ לטווח (${farStudents.length})`}
                            {farStudents.length > 0 && " ⚠️"}
                        </button>

                        {showFarPanel && (
                            <div style={expandedListStyle}>
                                {farStudents.length === 0 ? (
                                    <p style={{ color: '#28a745', textAlign: 'center', padding: '20px' }}>
                                        כל התלמידות בטווח תקין (עד 3 ק"מ מהמורה).
                                    </p>
                                ) : (
                                    <div style={{ overflowX: 'auto' }}>
                                        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'right' }}>
                                            <thead>
                                                <tr style={{ borderBottom: '2px solid #eee' }}>
                                                    <th style={{ padding: '12px' }}>תלמידה</th>
                                                    <th style={{ padding: '12px' }}>מרחק מהמורה</th>
                                                    <th style={{ padding: '12px' }}>מיקום (Lat, Lng)</th>
                                                    <th style={{ padding: '12px' }}>עדכון אחרון</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {farStudents.map(s => (
                                                    <tr key={s.student_tz} style={{ borderBottom: '1px solid #f8f9fa', background: '#fff' }}>
                                                        <td style={{ padding: '12px', fontWeight: 'bold' }}>{s.first_name} {s.last_name}</td>
                                                        <td style={{ padding: '12px', color: '#dc3545', fontWeight: 'bold' }}>{s.distance} ק"מ</td>
                                                        <td style={{ padding: '12px', fontSize: '12px', color: '#666' }}>
                                                            {s.latitude?.toFixed(5)}, {s.longitude?.toFixed(5)}
                                                        </td>
                                                        <td style={{ padding: '12px', fontSize: '13px' }}>
                                                            {new Date(s.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                                                        </td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    </div>
                                )}
                            </div>
                        )}
                    </section>
                </div>
            )}
        </div>
    );
};

// --- Styles ---
const containerStyle = { maxWidth: '1100px', margin: 'auto', padding: '20px', direction: 'rtl', fontFamily: 'system-ui, -apple-system, sans-serif' };
const feedbackStyle = { position: 'fixed', top: '20px', left: '50%', transform: 'translateX(-50%)', padding: '10px 25px', borderRadius: '8px', zIndex: 1000, fontWeight: 'bold', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' };
const headerStyle = { borderBottom: '2px solid #eee', marginBottom: '20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingBottom: '15px' };
const logoutBtnStyle = { background: '#dc3545', color: 'white', border: 'none', padding: '10px 20px', borderRadius: '5px', cursor: 'pointer', fontWeight: '500' };
const navStyle = { marginBottom: '25px', display: 'flex', gap: '10px' };
const navBtnStyle = { flex: 1, padding: '15px', border: '1px solid #ddd', borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold', transition: 'all 0.2s' };
const gridStyle = { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '30px' };
const cardStyle = { background: '#fff', padding: '25px', borderRadius: '12px', border: '1px solid #eee', boxShadow: '0 4px 6px rgba(0,0,0,0.02)' };
const sectionTitleStyle = { marginTop: 0, borderBottom: '2px solid #007bff', display: 'inline-block', paddingBottom: '5px', marginBottom: '20px' };
const inputStyle = { display: 'block', width: '100%', padding: '12px', marginBottom: '12px', border: '1px solid #ddd', borderRadius: '6px', boxSizing: 'border-box', fontSize: '14px' };
const submitBtnStyle = { width: '100%', padding: '12px', background: '#007bff', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold', marginTop: '10px' };
const listContainerStyle = { background: '#fff', border: '1px solid #eee', padding: '20px', borderRadius: '12px' };
const listItemStyle = { padding: '10px 0', borderBottom: '1px solid #f8f9fa' };
const toggleBtnStyle = { width: '100%', padding: '12px', marginTop: '10px', background: '#f8f9fa', border: '1px solid #ddd', borderRadius: '6px', cursor: 'pointer', textAlign: 'right', fontWeight: '600' };
const expandedListStyle = { marginTop: '10px', padding: '10px', maxHeight: '300px', overflowY: 'auto', border: '1px solid #f0f0f0', borderRadius: '6px' };
const searchBtnStyle = { background: '#343a40', color: 'white', border: 'none', padding: '0 20px', borderRadius: '6px', cursor: 'pointer' };
const resultCardStyle = { background: '#e7f3ff', padding: '15px', borderRadius: '8px', marginBottom: '15px', border: '1px solid #b3d7ff', fontSize: '14px' };
const mapWrapperStyle = { height: '550px', width: '100%', borderRadius: '15px', overflow: 'hidden', border: '1px solid #ddd', boxShadow: '0 2px 10px rgba(0,0,0,0.1)' };

export default Dashboard;