import { Component, OnInit, ViewChild, ElementRef, AfterViewInit, OnDestroy, inject } from '@angular/core';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatFormFieldModule } from '@angular/material/form-field';
import { FormsModule } from '@angular/forms';

import { Inject } from '@angular/core';

import {
  HttpClient,
  HttpHeaders,
  HttpErrorResponse
} from "@angular/common/http";
import { Map, NavigationControl, Marker, GeoJSONSource, Point } from 'maplibre-gl';
import { response } from 'express';
import { animate } from '@angular/animations';

const httpOptions = {
  headers: new HttpHeaders({ "Content-Type": "application/json" })
};

// @NgModule({
//   imports: [FormsModule],
// })

const images = {
  'popup': 'https://maplibre.org/maplibre-gl-js/docs/assets/popup.png',
  'popup-debug':
    'https://maplibre.org/maplibre-gl-js/docs/assets/popup_debug.png'
};



@Component({
  standalone: true,
  selector: 'app-map',
  templateUrl: './map.component.html',
  imports: [MatFormFieldModule, MatSelectModule, MatInputModule, FormsModule],
  styleUrls: ['./map.component.css']
})
export class MapComponent implements OnInit, AfterViewInit, OnDestroy {
  map: Map | undefined;

  @ViewChild('map')
  private mapContainer!: ElementRef<HTMLElement>;

  startValuePayload = {
    lat: 0,
    long: 0,
    locationString: '',
    isLatLongResolved: false
  }

  endValuePayload = {
    lat: 0,
    long: 0,
    locationString: '',
    isLatLongResolved: false
  }

  markers = new Array<Marker>();

  constructor(private http: HttpClient) {
  }

  ngOnInit(): void {
  }
  async ngAfterViewInit() {
    const initialState = { lng: 11.576124, lat: 48.137154, zoom: 15 };

    this.map = new Map({
      container: this.mapContainer.nativeElement,
      style: `assets/style.json`,
      center: [initialState.lng, initialState.lat],
      zoom: initialState.zoom
    });

    this.map.addControl(new NavigationControl());
    this.map.setPitch(45);

    const debugPopup = await this.map?.loadImage(images['popup-debug']);
    const popup = await this.map?.loadImage(images['popup']);

    this.map.addImage('popup-debug', debugPopup.data, {
      // The two (blue) columns of pixels that can be stretched horizontally:
      //   - the pixels between x: 25 and x: 55 can be stretched
      //   - the pixels between x: 85 and x: 115 can be stretched.
      stretchX: [
        [25, 55],
        [85, 115]
      ],
      // The one (red) row of pixels that can be stretched vertically:
      //   - the pixels between y: 25 and y: 100 can be stretched
      stretchY: [[25, 100]],
      // This part of the image that can contain text ([x1, y1, x2, y2]):
      content: [25, 25, 115, 100],
      // This is a high-dpi image:
      pixelRatio: 2
    });
    this.map.addImage('popup', popup.data, {
      stretchX: [
        [25, 55],
        [85, 115]
      ],
      stretchY: [[25, 100]],
      content: [25, 25, 115, 100],
      pixelRatio: 2
    });

  }

  ngOnDestroy() {
    this.map?.remove();
  }

  endpointValue = "";

  startPointLonLat = [0, 0]
  endPointLonLat = [0, 0]

  startPoint(event: any) {
    // this.startpointValue = event.target.value;
  }

  endPoint(event: any) {
    this.endpointValue = event.target.value;
  }

  initMap() {
    this.markers.forEach(marker => {
      marker.remove();
    });
    this.markers = new Array<Marker>();
  }

  buttonClick(event: any) {
    this.initMap();
    this.resolveLocations(this.startValuePayload);
    this.resolveLocations(this.endValuePayload);
    console.log(this.startPointLonLat, this.endPointLonLat);
  }

  sourceIDs = new Array<string>();
  sourceLabels = new Array<string>();

  getRandomColor() {
    var letters = '0123456789ABCDEF';
    var color = '#';
    for (var i = 0; i < 6; i++) {
      color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
  }



  async latLongInformationUpdatedEvent() {

    if (this.endValuePayload['isLatLongResolved'] === true) {
      console.log("Resolve directions here");
      let marker = new Marker({
        color: "#FFFFFF",
        draggable: true
      }).setLngLat([this.endValuePayload['long'], this.endValuePayload['lat']])
        .addTo(this.map as Map);

      let marker2 = new Marker({
        color: "#FFFFFF",
        draggable: true
      }).setLngLat([this.startValuePayload['long'], this.startValuePayload['lat']])
        .addTo(this.map as Map);

      this.markers.push(marker);
      this.markers.push(marker2);

      let postPayload = {
        "point1": [this.startValuePayload['long'], this.startValuePayload['lat']],
        "point2": [this.endValuePayload['long'], this.endValuePayload['lat']]
      };

      const headers = new HttpHeaders().set('Content-Type', 'application/json; charset=utf-8');

      console.log(postPayload)
      this.http.post("http://127.0.0.1:5001/route", JSON.stringify(postPayload), { headers: headers }).subscribe((response) => {

        let routePayload = JSON.parse(JSON.stringify(response))
        console.log(routePayload);


        this.sourceIDs.forEach(element => {
          (this.map?.getSource(element) as GeoJSONSource).setData({
            'type': 'Feature',
            'properties': {},
            'geometry': { type: "LineString", coordinates: [] }
          }
          );
        });

        this.sourceLabels.forEach(element => {
          (this.map?.getSource(element) as GeoJSONSource).setData({
            'type': 'Feature',
            'properties': {},
            'geometry': { type: "Point", coordinates: [] }
          }
          );
        });

        this.sourceIDs = new Array<string>();
        this.sourceLabels = new Array<string>();

        let count = 1;


        routePayload['processed_paths'].forEach((element: { [x: string]: { [x: string]: any; }; }) => {
          this.sourceIDs.push('routeMap_' + (count));
          this.sourceLabels.push('label_' + (count));
          let middleElement = structuredClone(element['geometryJSON']['geometry']['coordinates'][Math.round((element['geometryJSON']['geometry']['coordinates'].length - 1) / 2)])
          middleElement[1] *= 1;
          let labelString = 
          (Math.round((element['cumulative_polygon_distance'] as unknown as number) / 10) / 100) +
            " km\nCO2 Estimated: "
            + (Math.round((element['cumulative_co2_kg'] as unknown as number) *100) / 100)
            + " kg\nFuel Estimated: "
            + (Math.round((element['cumulative_fuel_l'] as unknown as number) *100) / 100)
            + " L\nAltitude Change: "
            + (Math.round((element['cumulative_altitude_change'] as unknown as number) *100) / 100) + "m";
          

          if (this.map?.getSource('routeMap_' + (count))) {
            (this.map?.getSource('routeMap_' + (count)) as GeoJSONSource).setData({
              'type': 'Feature',
              'properties': {},
              'geometry': element['geometryJSON']['geometry']
            })
          }
          else {
            this.map?.addSource('routeMap_' + (count), {
              'type': 'geojson',
              'data': {
                'type': 'Feature',
                'properties': {},
                'geometry': element['geometryJSON']['geometry']
              }
            });

            this.map?.addLayer({
              'id': 'routeMap_' + (count),
              'type': 'line',
              'source': 'routeMap_' + (count),
              'layout': {
                'line-join': 'round',
                'line-cap': 'round'
              },
              'paint': {
                // 'line-color': "#" + (9) + (9 - count) + (9),
                'line-color': this.getRandomColor(),
                'line-width': 8 - (count * 2)
              }
            });
          }

          if (this.map?.getSource('label_' + (count))) {

            (this.map?.getSource('label_' + (count)) as GeoJSONSource).setData(
              {
                'type': 'FeatureCollection',
                'features': [
                  {
                    'type': 'Feature',
                    'geometry': {
                      'type': 'Point',
                      'coordinates': middleElement
                    },
                    'properties': {
                      'image-name': 'popup',
                      'name': labelString
                    }
                  }
                ]
              }
            );
          }
          else {
            this.map?.addSource('label_' + (count), {
              'type': 'geojson',
              'data': {
                'type': 'FeatureCollection',
                'features': [
                  {
                    'type': 'Feature',
                    'geometry': {
                      'type': 'Point',
                      'coordinates': middleElement
                    },
                    'properties': {
                      'image-name': 'popup',
                      'name': labelString
                    }
                  }
                ]
              }
            });

            this.map?.addLayer({
              'id': 'labellayer_' + (count),
              'type': 'symbol',
              'source': 'label_' + (count),
              'layout': {
                'text-field': ['get', 'name'],
                'icon-text-fit': 'both',
                'icon-image': ['get', 'image-name'],
                'icon-overlap': 'always',
                'text-overlap': 'always'
              }
            });
          }
          count = count + 1;
        });

        let centreZoomBearing = this.map?.cameraForBounds([[this.endValuePayload['long'], this.endValuePayload['lat']], [this.startValuePayload['long'], this.startValuePayload['lat']]], {
          padding: { top: 100, bottom: 100, left: 100, right: 300 }
        });

        this.map?.flyTo({
          center: centreZoomBearing?.center,
          zoom: centreZoomBearing?.zoom,
          bearing: centreZoomBearing?.bearing, duration: 2500,
          essential: true
        });

      });
    }
  }

  resolveLocations(value: any) {
    this.http.get("https://nominatim.openstreetmap.org/search?format=json&q=" + value['locationString']).subscribe((response) => {
      console.log(response);
      let payload = JSON.parse(JSON.stringify(response))
      console.log(payload[0]['lat']);
      let lat = payload[0]['lat'];
      let long = payload[0]['lon'];
      value['long'] = long;
      value['lat'] = lat;
      value['locationString'] = payload[0]['display_name'];
      value['isLatLongResolved'] = true;
      this.latLongInformationUpdatedEvent();
    });
  }

}