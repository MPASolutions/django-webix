function onEachFeature(feature, layer) {

    // if (feature.properties && feature.properties.popupContent) {
    //      popupContent += feature.properties.popupContent;
    // }
    console.log('#',feature);
    layer.bindPopup(feature.name);
}

function extentToBounds(extent){
    var southWest = new L.LatLng(extent[1], extent[0]),
        northEast = new L.LatLng(extent[3], extent[2]),
        bounds = new L.LatLngBounds(southWest, northEast);
    return bounds;
}

function getCookie(name) {
    var value = "; " + document.cookie;
    var parts = value.split("; " + name + "=");
    if (parts.length == 2){
        return parts.pop().split(";").shift();
    }
    return '';
}

webix.protoUI({
    name:"open-map",
    $init:function(){
        this.$view.innerHTML = "<div class='webix_map_content' style='width:100%; height:100%'></div>";
        this._contentobj = this.$view.firstChild;
        this.map = null;
        this.$ready.push(this.render);
    },
    render:function(){
        // caricate nello header -> non fa il require di path assoluti
        if(!window.L || !window.L.map){
            webix.require([
                "../../lib/leaflet/leaflet.js",
                "../../lib/leaflet/leaflet.css",
                "../../lib/leaflet/leaflet.draw.js",
                "../../lib/leaflet/leaflet.draw.css",
                "../../lib/leaflet/easy-button.js",
                "../../lib/leaflet/easy-button.css"
            ], this._initMap, this);
        }
        else
        
            this._initMap();
    },
    _initMap:function(define){
        var c = this.config;
        this.map = L.map(this._contentobj);
        var map = this.map;

        if(c.extent){
            bounds = extentToBounds(c.extent);
            console.log("Fitbounds - extent " + c.extent);
            console.log("Fitbounds - bounds " + bounds);
            map.fitBounds(bounds, {maxZoom: 0, animate: true, maxZoom: 18});
        }

        if(c.fitBounds){
            map.fitBounds(c.fitBounds, {maxZoom: 18});
        }

        var editableLayer = L.geoJson(c.geojson, {
            style: {
                fillColor: "#ff7800",
                color: "#000",
                weight: 1,
                opacity: 1,
                fillOpacity: 0.3
            },
            onEachFeature: function (feature, layer) {
                // featureGroup.addLayer(layer);
                layer.bindPopup(feature.name);
            }
        }).addTo(map);
        console.log(c.geojson);
        // resolve layer alias
        var lastLayer;
        var layers = c.baseMaps;
        for(l in layers){
            if(layers.hasOwnProperty(l)){
                if(layers[l] == 'osm' ){
                    layers[l] = L.tileLayer(
                        'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                            maxZoom: 18,
                            attribution: '&copy; <a href="http://openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                        })
                }
                lastLayer = layers[l];
            }
        }

        lastLayer.addTo(map);

        L.control.layers(c.baseMaps,
                         c.overlayMaps, {
            position: 'topleft',
            collapsed: false }).addTo(map);

        if(c.saveUrl && (typeof c.controlType != "undefined")){
            map.addControl(new L.Control.Draw({
                edit: {
                    featureGroup: editableLayer,
                    poly : {
                        allowIntersection : false
                    },
                    edit: {
                        selectedPathOptions: {
                            fillColor: "#ff7800",
                            color: "#000",
                            weight: 1,
                            opacity: 0.5,
                            fillOpacity: 0.3
                        }
                    }
                },
                draw: {
                    polygon: false,
                    polyline: false,
                    rectangle: false,
                    circle: false,
                    marker: c.controlType == 'marker' ? true : false
                }
            }));

            L.easyButton( '<span class="save">S</span>', function(){
                $.ajax({
                    url: c.saveUrl + c.pk + "/updategeo",
                    //dataType: "json",
                    contentType: "application/json",
                    dataType: 'json',
                    method: "POST",
                    data: JSON.stringify(editableLayer.toGeoJSON()),
                    success: function(data){
                        if(data.status){
                            alert("La geometria e' stata salvata");
                        } else {
                            alert("Non e' possibile salvare la geometria");
                        }
                    }
                });
            }).addTo(map);

            map.on('draw:created', function(event) {
                var layer = event.layer;

                editableLayer.addLayer(layer);

            });

        } else if (c.saveUrl) {
            map.addControl(new L.Control.Draw({
                edit: {
                    featureGroup: editableLayer,
                    poly : {
                        allowIntersection : false
                    },
                    edit: {
                        selectedPathOptions: {
                            fillColor: "#ff7800",
                            color: "#000",
                            weight: 1,
                            opacity: 0.5,
                            fillOpacity: 0.3
                        }
                    }
                },
                draw: {
                    polygon : {
                        allowIntersection: false,
                        showArea: true,
                        shapeOptions: {
                            fillColor: "#ff7800",
                            color: "#000",
                            weight: 1,
                            opacity: 0.5,
                            fillOpacity: 0.8
                        }
                    },
                    polyline: false,
                    rectangle: false,
                    circle: false,
                    marker: false
                }
            }));

            L.easyButton( '<span class="save">S</span>', function(){
                $.ajax({
                    url: c.saveUrl + c.pk + "/updategeo",
                    //dataType: "json",
                    contentType: "application/json",
                    dataType: 'json',
                    method: "POST",
                    data: JSON.stringify(editableLayer.toGeoJSON()),
                    success: function(data){
                        if(data.status){
                            alert("La geometria e' stata salvata");
                        } else {
                            alert("Non e' possibile salvare la geometria");
                        }
                    }
                });
            }).addTo(map);

            map.on('draw:created', function(event) {
                var layer = event.layer;

                editableLayer.addLayer(layer);

            });
        }
    },
    center_setter:function(config){
        if(this.map)
            this.map.setCenter(config);

        return config;
    },
    mapType_setter:function(config){
        //yadex#map, yadex#satellite, yadex#hybrid, yadex#publicMap
        if(this.map)
            this.map.setType(config);

        return config;
    },
    zoom_setter:function(config){
        if(this.map)
            this.map.setZoom(config);

        return config;
    },
    fitBounds_setter:function(config){
        if(this.map)
            this.map.fitBounds(config);

        return config;
    },
    geojson_setter:function(config){
        if(this.map)
            this.map.fitBounds(config);

        return config;
    },
    defaults:{
        zoom: 5,
        center:[ 0, 0 ],
        geojson: [],
        fitBounds: false,
        extent: [10, 40 , 15, 45],
        baseMaps: {
            "OpenStreetMap": "osm"
        }
    }
}, webix.ui.view, webix.EventSystem);
