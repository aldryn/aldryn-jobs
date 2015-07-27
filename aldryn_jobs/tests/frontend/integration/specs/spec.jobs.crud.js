/*!
 * @author:    Divio AG
 * @copyright: http://www.divio.ch
 */

'use strict';
/* global describe, it, browser */

// #############################################################################
// INTEGRATION TEST
var jobsPage = require('../pages/page.jobs.crud.js');

describe('Aldryn Jobs tests: ', function () {
    it('opens the main page', function () {
        // go to the main page
        browser.get(jobsPage.site);
    });

});
