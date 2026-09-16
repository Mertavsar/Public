import {Config} from '@remotion/cli/config';
import {findLocalChrome} from './scripts/find-chrome.mjs';

Config.setVideoImageFormat('jpeg');
Config.setOverwriteOutput(true);
// Shorts'ta metin kenarlari kritik; YouTube yeniden kodladiktan sonra
// bozulmamasi icin crf dusuk tutulur.
Config.setCrf(18);

// Bu dosya sadece CLI tarafindan okunur. Node API (scripts/render-batch.mjs)
// ayni yolu kendisi gecirir.
const chrome = findLocalChrome();
if (chrome) {
  Config.setBrowserExecutable(chrome);
}
