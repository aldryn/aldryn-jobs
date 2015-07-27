/*!
 * @author:    Divio AG
 * @copyright: http://www.divio.ch
 */

'use strict';
/* global describe, it, browser, By, expect */

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

    it('creates a new test page', function () {
        // click the example.com link in the top menu
        jobsPage.userMenus.first().click().then(function () {
            // wait for top menu dropdown options to appear
            browser.wait(function () {
                return browser.isElementPresent(jobsPage.userMenuDropdown);
            }, jobsPage.mainElementsWaitTime);

            return jobsPage.administrationOptions.first().click();
        }).then(function () {
            // wait for modal iframe to appear
            browser.wait(function () {
                return browser.isElementPresent(jobsPage.sideMenuIframe);
            }, jobsPage.iframeWaitTime);

            // switch to sidebar menu iframe
            browser.switchTo().frame(browser.findElement(
                By.css('.cms_sideframe-frame iframe')));

            browser.wait(function () {
                return browser.isElementPresent(jobsPage.pagesLink);
            }, jobsPage.mainElementsWaitTime);

            jobsPage.pagesLink.click();

            // wait for iframe side menu to reload
            browser.wait(function () {
                return browser.isElementPresent(jobsPage.addConfigsButton);
            }, jobsPage.mainElementsWaitTime);

            // check if the page already exists and return the status
            return jobsPage.addPageLink.isPresent();
        }).then(function (present) {
            if (present === true) {
                // page is absent - create new page
                browser.wait(function () {
                    return browser.isElementPresent(jobsPage.addPageLink);
                }, jobsPage.mainElementsWaitTime);

                jobsPage.addPageLink.click();

                browser.wait(function () {
                    return browser.isElementPresent(jobsPage.titleInput);
                }, jobsPage.mainElementsWaitTime);

                jobsPage.titleInput.sendKeys('Test').then(function () {
                    jobsPage.saveButton.click();

                    return jobsPage.slugErrorNotification.isPresent();
                }).then(function (present) {
                    if (present === false) {
                        browser.wait(function () {
                            return browser.isElementPresent(jobsPage.editPageLink);
                        }, jobsPage.mainElementsWaitTime);

                        // wait till the editPageLink will become clickable
                        browser.sleep(500);

                        // validate/click edit page link
                        jobsPage.editPageLink.click();

                        // switch to default page content
                        browser.switchTo().defaultContent();

                        browser.wait(function () {
                            return browser.isElementPresent(jobsPage.testLink);
                        }, jobsPage.mainElementsWaitTime);

                        // validate test link text
                        jobsPage.testLink.getText().then(function (title) {
                            expect(title).toEqual('Test');
                        });
                    }
                });
            }
        });
    });

});
