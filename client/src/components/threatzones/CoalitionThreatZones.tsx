import { ThreatZoneFilter, ThreatZonesLayer } from "./ThreatZonesLayer";
import { LayersControl } from "react-leaflet";

interface CoalitionThreatZonesProps {
  blue: boolean;
}

export function CoalitionThreatZones(props: CoalitionThreatZonesProps) {
  const color = props.blue ? "синих" : "красных";
  return (
    <>
      <LayersControl.Overlay name={`Зоны угроз ${color}: все`}>
        <ThreatZonesLayer blue={props.blue} filter={ThreatZoneFilter.FULL} />
      </LayersControl.Overlay>
      <LayersControl.Overlay name={`Зоны угроз ${color}: авиация`}>
        <ThreatZonesLayer
          blue={props.blue}
          filter={ThreatZoneFilter.AIRCRAFT}
        />
      </LayersControl.Overlay>
      <LayersControl.Overlay name={`Зоны угроз ${color}: ПВО`}>
        <ThreatZonesLayer
          blue={props.blue}
          filter={ThreatZoneFilter.AIR_DEFENSES}
        />
      </LayersControl.Overlay>
      <LayersControl.Overlay name={`Зоны угроз ${color}: ЗРК с РЛС`}>
        <ThreatZonesLayer
          blue={props.blue}
          filter={ThreatZoneFilter.RADAR_SAMS}
        />
      </LayersControl.Overlay>
    </>
  );
}
