mapboxgl.accessToken = 'pk.eyJ1IjoibWFhcm91ZiIsImEiOiJjajNzcmlicTcwMDF6MndwNnp2bnlrcjl6In0.Lx6E2KTnK0ko1OeSrLDZDA';
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