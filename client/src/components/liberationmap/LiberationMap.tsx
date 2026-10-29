import { selectMapCenter } from "../../api/mapSlice";
import { useAppSelector } from "../../app/hooks";
import AircraftLayer from "../aircraftlayer";
import AirDefenseRangeLayer from "../airdefenserangelayer";
import CombatLayer from "../combatlayer";
import ControlPointsLayer from "../controlpointslayer";
import CullingExclusionZones from "../cullingexclusionzones/CullingExclusionZones";
import FlightPlansLayer from "../flightplanslayer";
import FrontLinesLayer from "../frontlineslayer";
import Iadsnetworklayer from "../iadsnetworklayer";
import NavMeshLayer from "../navmesh/NavMeshLayer";
import LeafletRuler from "../ruler/Ruler";
import SupplyRoutesLayer from "../supplyrouteslayer";
import TerrainZonesLayers from "../terrainzones/TerrainZonesLayers";
import TgosLayer from "../tgoslayer/TgosLayer";
import { CoalitionThreatZones } from "../threatzones";
import { WaypointDebugZonesControls } from "../waypointdebugzones/WaypointDebugZonesControls";
import "./LiberationMap.css";
import { Map } from "leaflet";
import { useEffect, useRef } from "react";
import { BasemapLayer } from "react-esri-leaflet";
import { LayersControl, MapContainer, ScaleControl } from "react-leaflet";

export default function LiberationMap() {
  const map = useRef<Map>(null);
  const mapCenter = useAppSelector(selectMapCenter);
  useEffect(() => {
    map.current?.setView(mapCenter, 8, { animate: true, duration: 1 });
  });
  return (
    <MapContainer zoom={8} zoomControl={false} ref={map}>
      <ScaleControl />
      <LeafletRuler />
      <LayersControl collapsed={false}>
        <LayersControl.BaseLayer name="Спутник (Clarity)" checked>
          <BasemapLayer name="ImageryClarity" />
        </LayersControl.BaseLayer>
        <LayersControl.BaseLayer name="Спутник (Firefly)">
          <BasemapLayer name="ImageryFirefly" />
        </LayersControl.BaseLayer>
        <LayersControl.BaseLayer name="Топографическая">
          <BasemapLayer name="Topographic" />
        </LayersControl.BaseLayer>
        <LayersControl.Overlay name="Контрольные точки" checked>
          <ControlPointsLayer />
        </LayersControl.Overlay>
        <LayersControl.Overlay name="Авиация" checked>
          <AircraftLayer />
        </LayersControl.Overlay>
        <LayersControl.Overlay name="Активные бои" checked>
          <CombatLayer />
        </LayersControl.Overlay>
        <LayersControl.Overlay name="ПВО" checked>
          <TgosLayer categories={["aa"]} />
        </LayersControl.Overlay>
        <LayersControl.Overlay name="Заводы" checked>
          <TgosLayer categories={["factory"]} />
        </LayersControl.Overlay>
        <LayersControl.Overlay name="Корабли" checked>
          <TgosLayer categories={["ship"]} />
        </LayersControl.Overlay>
        <LayersControl.Overlay name="Прочие наземные объекты" checked>
          <TgosLayer categories={["aa", "factory", "ship"]} exclude />
        </LayersControl.Overlay>
        <LayersControl.Overlay name="Пути снабжения" checked>
          <SupplyRoutesLayer />
        </LayersControl.Overlay>
        <LayersControl.Overlay name="Линии фронта" checked>
          <FrontLinesLayer />
        </LayersControl.Overlay>
        <LayersControl.Overlay name="Зона поражения ЗРК противника" checked>
          <AirDefenseRangeLayer blue={false} />
        </LayersControl.Overlay>
        <LayersControl.Overlay name="Зона обнаружения ЗРК противника">
          <AirDefenseRangeLayer blue={false} detection />
        </LayersControl.Overlay>
        <LayersControl.Overlay name="Сеть ПВО противника">
          <Iadsnetworklayer blue={false} />
        </LayersControl.Overlay>
        <LayersControl.Overlay name="Зона поражения союзных ЗРК">
          <AirDefenseRangeLayer blue={true} />
        </LayersControl.Overlay>
        <LayersControl.Overlay name="Зона обнаружения союзных ЗРК">
          <AirDefenseRangeLayer blue={true} detection />
        </LayersControl.Overlay>
        <LayersControl.Overlay name="Союзная сеть ПВО">
          <Iadsnetworklayer blue={true} />
        </LayersControl.Overlay>
        <LayersControl.Overlay name="Выбранный план полёта синих">
          <FlightPlansLayer blue={true} selectedOnly />
        </LayersControl.Overlay>
        <LayersControl.Overlay name="Все планы полётов синих" checked>
          <FlightPlansLayer blue={true} />
        </LayersControl.Overlay>
        <LayersControl.Overlay name="Все планы полётов красных">
          <FlightPlansLayer blue={false} />
        </LayersControl.Overlay>
      </LayersControl>
      <LayersControl position="topleft">
        <CoalitionThreatZones blue={true} />
        <CoalitionThreatZones blue={false} />
        <LayersControl.Overlay name="Навсетка синих">
          <NavMeshLayer blue={true} />
        </LayersControl.Overlay>
        <LayersControl.Overlay name="Навсетка красных">
          <NavMeshLayer blue={false} />
        </LayersControl.Overlay>
        <TerrainZonesLayers />
        <CullingExclusionZones />
        <WaypointDebugZonesControls />
      </LayersControl>
    </MapContainer>
  );
}
