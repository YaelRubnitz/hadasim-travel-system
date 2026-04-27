import { useState, useEffect } from 'react';
import api from '../api/axios';
import MapComponent from '../components/MapComponent';

const Dashboard = ({ teacher, onLogout }) => {
    const [view, setView] = useState('manage'); 
    const [myStudents, setMyStudents] = useState([]);
    const [allTeachers, setAllTeachers] = useState([]);
    const [allStudents, setAllStudents] = useState([]);
    
    const [showMyStudents, setShowMyStudents] = useState(true);
    const [showAllTeachers, setShowAllTeachers] = useState(false);
    const [showAllStudents, setShowAllStudents] = useState(false);
    
    const [message, setMessage] = useState({ text: '', type: '' });
    
    const [searchTz, setSearchTz] = useState('');
    const [singleResult, setSingleResult] = useState(null);

    const [newStudent, setNewStudent] = useState({ tz: '', first_name: '', last_name: '' });
    const [newTeacher, setNewTeacher] = useState({ id_number: '', first_name: '', last_name: '', class_name: '' });

    const showFeedback = (text, type = 'success') => {
        setMessage({ text, type });
        setTimeout(() => setMessage({ text: '', type: '' }), 3000);
    };

    const fetchData = async () => {
        try {
            const [myClassRes, allTeachersRes, allStudentsRes, locationsRes] = await Promise.all([
                api.get('/students/my-class'),
                api.get('/teachers/'),
                api.get('/students/'),
                api.get('/locations/class-last-locations')
            ]);
            
            const studentsWithLoc = myClassRes.data.map(s => {
                const loc = locationsRes.data.find(l => l.student_tz?.toString() === s.tz?.toString());
                return loc ? { ...s, latitude: loc.latitude, longitude: loc.longitude } : s;
            });
            
            setMyStudents(studentsWithLoc);
            setAllTeachers(allTeachersRes.data);
            setAllStudents(allStudentsRes.data);
        } catch (err) { console.error("Error fetching data:", err); }
    };

    useEffect(() => {
        fetchData(); 

       const interval = setInterval(() => {
            fetchData(); 
        }, 60000); 

        return () => {
            clearInterval(interval);
        };
    }, []); 
  

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
            fetchData();
            showFeedback("התלמידה נוספה בהצלחה!");
        } catch (err) { showFeedback("שגיאה בהוספת תלמידה", "error"); }
    };

    const handleAddTeacher = async (e) => {
        e.preventDefault();
        try {
            await api.post('/teachers/', {
                tz: newTeacher.tz, 
                first_name: newTeacher.first_name,
                last_name: newTeacher.last_name,
                class_name: newTeacher.class_name
            });
            setNewTeacher({ tz: '', first_name: '', last_name: '', class_name: '' });
            fetchData();
            showFeedback("המורה נוספ/ה בהצלחה!");
        } catch (err) { showFeedback("שגיאה בהוספת מורה", "error"); }
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
                <div style={mapWrapperStyle}>
                    <MapComponent students={myStudents} />
                </div>
            )}
        </div>
    );
};

// Styles (נשארים בדיוק כפי שהיו)
const containerStyle = { maxWidth: '1100px', margin: 'auto', padding: '20px', direction: 'rtl', fontFamily: 'Arial' };
const feedbackStyle = { position: 'fixed', top: '20px', left: '50%', transform: 'translateX(-50%)', padding: '10px 25px', borderRadius: '8px', zIndex: 1000, fontWeight: 'bold', boxShadow: '0 4px 6px rgba(0,0,0,0.1)' };
const headerStyle = { borderBottom: '2px solid #eee', marginBottom: '20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingBottom: '15px' };
const logoutBtnStyle = { background: '#ff4444', color: 'white', border: 'none', padding: '10px 20px', borderRadius: '5px', cursor: 'pointer' };
const navStyle = { marginBottom: '25px', display: 'flex', gap: '10px' };
const navBtnStyle = { flex: 1, padding: '15px', border: '1px solid #ddd', borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold' };
const gridStyle = { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '30px' };
const cardStyle = { background: '#f9f9f9', padding: '25px', borderRadius: '12px', border: '1px solid #eee', boxShadow: '0 2px 8px rgba(0,0,0,0.05)' };
const sectionTitleStyle = { marginTop: 0, borderBottom: '2px solid #007bff', display: 'inline-block', paddingBottom: '5px' };
const inputStyle = { display: 'block', width: '100%', padding: '12px', marginBottom: '12px', border: '1px solid #ccc', borderRadius: '6px', boxSizing: 'border-box' };
const submitBtnStyle = { width: '100%', padding: '12px', background: '#007bff', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' };
const listContainerStyle = { background: 'white', border: '1px solid #eee', padding: '20px', borderRadius: '12px' };
const listItemStyle = { padding: '10px 0', borderBottom: '1px solid #f1f1f1' };
const toggleBtnStyle = { width: '100%', padding: '10px', marginTop: '10px', background: '#f8f9fa', border: '1px solid #ddd', borderRadius: '6px', cursor: 'pointer', textAlign: 'right', fontWeight: 'bold' };
const expandedListStyle = { marginTop: '10px', padding: '10px', maxHeight: '200px', overflowY: 'auto', border: '1px solid #f0f0f0' };
const searchBtnStyle = { background: '#333', color: 'white', border: 'none', padding: '0 20px', borderRadius: '6px', cursor: 'pointer' };
const resultCardStyle = { background: '#e7f3ff', padding: '15px', borderRadius: '8px', marginBottom: '15px', border: '1px solid #b3d7ff' };
const mapWrapperStyle = { height: '600px', width: '100%', borderRadius: '15px', overflow: 'hidden', border: '2px solid #ddd' };

export default Dashboard;