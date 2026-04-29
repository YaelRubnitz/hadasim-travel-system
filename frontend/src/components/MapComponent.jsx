import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import { useEffect } from 'react';

import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

let DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41]
});
L.Marker.prototype.options.icon = DefaultIcon;

const MapUpdater = ({ center }) => {
    const map = useMap();
    useEffect(() => {
        if (center) {
            map.setView(center, map.getZoom(), { animate: true });
        }
    }, [center, map]);
    return null;
};

const MapComponent = ({ students }) => {
    const studentWithLocation = students.find(
        (s) => s.latitude != null && s.longitude != null
    );

    const center = studentWithLocation 
        ? [studentWithLocation.latitude, studentWithLocation.longitude] 
        : [31.7683, 35.2137];

    return (
        <div style={{ height: "100%", width: "100%" }}>
            <MapContainer 
                center={center} 
                zoom={13} 
                style={{ height: "100%", width: "100%" }}
                zoomControl={true}
            >
                <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
                
                {/* מעדכן את המיקום בצורה חלקה */}
                <MapUpdater center={center} />

                {students.map((student) => {
                    if (student.latitude != null && student.longitude != null) {
                        return (
                            <Marker 
                                key={student.tz} 
                                position={[student.latitude, student.longitude]}
                            >
                                <Popup>
                                    <div style={{ textAlign: 'right', direction: 'rtl' }}>
                                        <strong>{student.first_name} {student.last_name}</strong> <br />
                                        ת"ז: {student.tz}
                                    </div>
                                </Popup>
                            </Marker>
                        );
                    }
                    return null;
                })}
            </MapContainer>
        </div>
    );
};

export default MapComponent;