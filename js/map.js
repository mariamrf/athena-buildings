mapboxgl.accessToken = 'pk.eyJ1IjoibWFhcm91ZiIsImEiOiJjajkxbnJuaXoyaXgwMnFyMDViZmNkaWc1In0.IXP3SdK0YZ9j7D0l6UDzsg';
var map = new mapboxgl.Map({
    container: 'map',
    center: [-21.827774, 64.128288],
    zoom: 12,
    style: 'mapbox://styles/mapbox/light-v9'
});

map.addControl(new mapboxgl.NavigationControl());

map.on('load', function(){
	map.addSource('buildings', {
		type: 'geojson',
		data: './geojson/iceland_buildings.geojson'
	});

	map.addLayer({
        "id": "buildings-boundary",
        "type": "fill",
        "source": "buildings",
        "paint": {
            "fill-color": "#D4AF37",
            "fill-opacity": 0.8
        }
    });
});