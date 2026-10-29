import { selectSelectedFlightId } from "../../api/flightsSlice";
import { useAppSelector } from "../../app/hooks";
import { HoldZonesLayer } from "./HoldZones";
import { JoinZonesLayer } from "./JoinZones";
import { LayersControl } from "react-leaflet";

const ENABLE_EXPENSIVE_DEBUG_TOOLS = false;

export function WaypointDebugZonesControls() {
  const selectedFlightId = useAppSelector(selectSelectedFlightId);

  if (!ENABLE_EXPENSIVE_DEBUG_TOOLS) {
    return <></>;
  }

  return (
    <>
      <LayersControl.Overlay name="Зоны сбора">
        <JoinZonesLayer flightId={selectedFlightId} />
      </LayersControl.Overlay>
      <LayersControl.Overlay name="Зоны ожидания">
        <HoldZonesLayer flightId={selectedFlightId} />
      </LayersControl.Overlay>
    </>
  );
}
