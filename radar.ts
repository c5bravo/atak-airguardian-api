import { Elysia } from "elysia";
import { forward } from "mgrs";
type State = [
  string, // icao24
  string, // callsign
  string, // origin_country
  number, // time_position
  number, // last_contact
  number, // longitude
  number, // latitude
  number, // baro_altitude
  boolean, // on_ground
  number, // velocity
  number, // true_track
  number, // vertical_rate
  Array<number>, // sensors
  number, // geo_altitude
  string, // squawk
  boolean, // spi
  0 | 1 | 2 | 3, // position_source
  number // category
];

type Response = {
  time: number;
  states: Array<State>;
};

async function fetchOpenSkyData() {
  const resp = await fetch(
    "https://opensky-network.org/api/states/all?lamin=59.5&lamax=70.0&lomin=19.5&lomax=31.5"
  );
  return (await resp.json()) as Response;
}

export const radarRouter = new Elysia({ prefix: "/radar", name: "radar" }).get(
  "/aircraft",
  async () => {
    const data = await fetchOpenSkyData();

    const map = data.states
      .filter((state) => !state[8])
      .map((state) => {
        const speed =
          state[9] < 140 ? "slow" : state[9] < 280 ? "fast" : "supersonic";
        const altitude =
          state[7] < 300 ? "surface" : state[7] < 3000 ? "low" : "high";
        const location = forward([state[5], state[6]], 1);

        return {
          id: 0,
          aircraftId: state[0],
          approximatePosition: location.substring(0, 3),
          generalPosition: location.substring(3, 5),
          accuratePosition: location.substring(5),
          speed,
          direction: Math.round(state[10]),
          altitude,
          details: state[2],
        };
      })
      .toSorted((a, b) => a.aircraftId.localeCompare(b.aircraftId));

    return map;
  }
);
