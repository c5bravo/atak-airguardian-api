import { env } from "bun";
import { Elysia, status } from "elysia";
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

async function fetchOpenSkyData(token: string) {
  const resp = await fetch(
    "https://opensky-network.org/api/states/all?lamin=59.5&lamax=70.0&lomin=19.5&lomax=31.5",
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );
  console.log(resp.headers.get("x-rate-limit-remaining"));
  if (!resp.ok) {
    console.log(resp.headers.get("x-rate-limit-retry-after-seconds"));

    return resp.status;
  }

  return (await resp.json()) as Response;
}

async function fetchToken() {
  const response = await fetch(
    "https://auth.opensky-network.org/auth/realms/opensky-network/protocol/openid-connect/token",
    {
      method: "POST",
      headers: { "content-type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({
        grant_type: "client_credentials",
        client_id: env.OPENSKY_CLIENT_ID!,
        client_secret: env.OPENSKY_CLIENT_SECRET!,
      }),
    }
  );
  const data = (await response.json()) as {
    access_token: string;
    expires_in: number;
  };
  return {
    access_token: data.access_token,
    expires_on: new Date().getTime() + data.expires_in,
  };
}

export const radarRouter = new Elysia({ prefix: "/radar", name: "radar" })
  .state("auth", { access_token: "", expires_on: 0 })
  .get("/aircraft", async ({ store }) => {
    try {
      if (store.auth.expires_on < new Date().getTime()) {
        const auth = await fetchToken();
        store.auth.access_token = auth.access_token;
        store.auth.expires_on = auth.expires_on;
      }

      const data = await fetchOpenSkyData(store.auth.access_token);
      if (typeof data === "number") {
        return status(data);
      }

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
            aircraftId: state[1],
            position: location,
            speed,
            direction: Math.round(state[10]),
            altitude,
            details: state[2],
          };
        })
        .toSorted((a, b) => a.aircraftId.localeCompare(b.aircraftId));

      return map;
    } catch (e) {
      console.error(e);
      return status(500);
    }
  });
