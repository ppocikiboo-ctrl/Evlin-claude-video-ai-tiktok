import {Config} from '@remotion/cli/config';

// Full HD H.264 export. Bitrate, audio codec and JPEG quality are set on the
// render command in package.json so they are visible in one place.
Config.setVideoImageFormat('jpeg');
Config.setOverwriteOutput(true);
Config.setConcurrency(null);

// Use an already-installed Chrome Headless Shell if one is provided,
// otherwise Remotion downloads its own on first render.
if (process.env.REMOTION_BROWSER) {
  Config.setBrowserExecutable(process.env.REMOTION_BROWSER);
}
