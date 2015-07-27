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
    it('logs in to the site with valid username and password', function () {
        // go to the main page
        browser.get(jobsPage.site);

        // check if the page already exists
        jobsPage.testLink.isPresent().then(function (present) {
            if (present === true) {
                // go to the main page
                browser.get(jobsPage.site + '?edit');
            } else {
                // click edit mode link
                jobsPage.editModeLink.click();
            }

            // wait for username input to appear
            browser.wait(function () {
                return browser.isElementPresent(jobsPage.usernameInput);
            }, jobsPage.mainElementsWaitTime);

            // login to the site
            jobsPage.cmsLogin();
        });
    });

});
