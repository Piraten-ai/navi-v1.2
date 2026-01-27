import { CircleMarker, Tooltip } from 'react-leaflet'
import type { CircleMarkerProps, TooltipProps } from 'react-leaflet'

interface Position {
  latitude: number
  longitude: number
}

interface CPA {
  distance_nm: number
  time_to_min: number
}

interface AisTarget {
  mmsi: string
  name?: string
  position?: Position
  sog?: number
  cog?: number
  cpa?: CPA
}

interface AISOverlayProps {
  targets: AisTarget[]
}

export function AISOverlay({ targets }: AISOverlayProps) {
  return (
    <>
      {targets.map((target) => {
        if (!target.position) return null
        const { latitude, longitude } = target.position
        const cpaDistance = target.cpa?.distance_nm || Infinity
        const isClose = cpaDistance < 1
        const isVeryClose = cpaDistance < 0.5

        const color = isVeryClose ? '#ff0000' : isClose ? '#ff6600' : '#ffff00'
        const radius = isVeryClose ? 12 : isClose ? 10 : 8

        return (
          <CircleMarker
            key={target.mmsi}
            {...({
              center: [latitude, longitude] as [number, number],
              radius,
              pathOptions: {
                color: color,
                fillColor: color,
                fillOpacity: 0.7,
                weight: isVeryClose ? 3 : 2
              }
            } as CircleMarkerProps)}
          >
            <Tooltip {...({ permanent: false } as TooltipProps)}>
              <div className="font-sans text-xs">
                <p className="font-semibold">{target.name || `Vessel ${target.mmsi}`}</p>
                <p>SOG: {target.sog?.toFixed(1) || '--'} kn</p>
                <p>COG: {target.cog?.toFixed(0) || '--'}°</p>
                {target.cpa && (
                  <p className={isClose ? 'text-red-600 font-bold' : ''}>
                    CPA: {target.cpa.distance_nm.toFixed(1)} NM in {target.cpa.time_to_min.toFixed(0)} min
                  </p>
                )}
              </div>
            </Tooltip>
          </CircleMarker>
        )
      })}
    </>
  )
}
