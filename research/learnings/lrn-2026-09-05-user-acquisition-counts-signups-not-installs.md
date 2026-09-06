---
id: lrn-2026-09-05-user-acquisition-counts-signups-not-installs
subject: tracking
claim: Riteangle's own user_acquisition table counts SIGN-UPS, not installs and not
  first opens, so there is no per-ad install count anywhere in the stack. The row
  is written by pocket-dating-coach's /api/attribution/install, which requires a Bearer
  session and keys the row on user_id; mobile/lib/attribution.dart's reportAcquisitionIfPending
  returns early while currentSession is null. Play Console has installs but cannot
  break them down by ad (no UTM dimension); we have per-ad detail but our earliest
  observable event is a completed signup. Play's own 28-day funnel was 139 device
  acquisitions -> 71 device first opens, so roughly half of installers never even
  open the app and a further unknown share never sign up. Reporting user_acquisition
  counts as 'installs per ad' is not approximately right, it is a different metric.
  Cost-per-install is not computable from this repo's data; cost-per-signup is.
source: source-code
confidence: high
sample_n: null
status: open
created: '2026-09-05'
last_confirmed: '2026-09-05'
review_after: '2026-11-04'
derived_from: null
questions: []
recs: []
promoted_to: null
---

## Claim

Riteangle's own user_acquisition table counts SIGN-UPS, not installs and not first opens, so there is no per-ad install count anywhere in the stack. The row is written by pocket-dating-coach's /api/attribution/install, which requires a Bearer session and keys the row on user_id; mobile/lib/attribution.dart's reportAcquisitionIfPending returns early while currentSession is null. Play Console has installs but cannot break them down by ad (no UTM dimension); we have per-ad detail but our earliest observable event is a completed signup. Play's own 28-day funnel was 139 device acquisitions -> 71 device first opens, so roughly half of installers never even open the app and a further unknown share never sign up. Reporting user_acquisition counts as 'installs per ad' is not approximately right, it is a different metric. Cost-per-install is not computable from this repo's data; cost-per-signup is.

## Evidence

- (2026-09-05) Read 2026-09-05 in pocket-dating-coach: mobile/lib/attribution.dart (captureInstallReferrer keeps the whole referrer and every utm_* plus ra_lp via the android_play_install_referrer package - the Install Referrer API, not the deprecated broadcast - but reportAcquisitionIfPending gates the POST on an authenticated Supabase session), and src/routes/api/attribution/install/+server.ts (401 without a Bearer token, row keyed on user.id). Funnel figures read the same day in Play Console for com.riteangle.app: 139 device acquisitions, 71 device first opens, 28-day window.
