/*!
 * @author:    Divio AG
 * @copyright: http://www.divio.ch
 */

'use strict';
/* global describe, it, browser, By, expect */

// #############################################################################
// INTEGRATION TEST
var jobsPage = require('../pages/page.jobs.crud.js');
var cmsProtractorHelper = require('cms-protractor-helper');

describe('Aldryn Jobs tests: ', function () {
    // create random job name
    var jobName = 'Test job ' + cmsProtractorHelper.randomDigits(4);

    it('logs in to the site with valid username and password', function () {
        // go to the main page
        browser.get(jobsPage.site);

        // check if the page already exists
        jobsPage.testLink.isPresent().then(function (present) {
            if (present === true) {
                // go to the main page
                browser.get(jobsPage.site + '?edit');
                browser.sleep(1000);
                cmsProtractorHelper.waitForDisplayed(jobsPage.usernameInput);
            }

            // login to the site
            jobsPage.cmsLogin();
        });
    });

    it('creates a new test page', function () {
        // close the wizard if necessary
        jobsPage.modalCloseButton.isDisplayed().then(function (displayed) {
            if (displayed) {
                jobsPage.modalCloseButton.click();
            }
        });

        cmsProtractorHelper.waitForDisplayed(jobsPage.userMenus.first());
        // have to wait till animation finished
        browser.sleep(300);
        // click the example.com link in the top menu
        jobsPage.userMenus.first().click().then(function () {
            // wait for top menu dropdown options to appear
            cmsProtractorHelper.waitForDisplayed(jobsPage.userMenuDropdown);

            return jobsPage.administrationOptions.first().click();
        }).then(function () {
            // wait for modal iframe to appear
            cmsProtractorHelper.waitFor(jobsPage.sideMenuIframe);

            // switch to sidebar menu iframe
            browser.switchTo().frame(browser.findElement(
                By.css('.cms-sideframe-frame iframe')));

            cmsProtractorHelper.waitFor(jobsPage.pagesLink);

            jobsPage.pagesLink.click();

            // wait for iframe side menu to reload
            cmsProtractorHelper.waitFor(jobsPage.addConfigsButton);

            // check if the page already exists and return the status
            return jobsPage.addPageLink.isPresent();
        }).then(function (present) {
            if (present === true) {
                // page is absent - create new page
                cmsProtractorHelper.waitFor(jobsPage.addPageLink);

                jobsPage.addPageLink.click();

                cmsProtractorHelper.waitFor(jobsPage.titleInput);

                jobsPage.titleInput.sendKeys('Test').then(function () {
                    jobsPage.saveButton.click();

                    return jobsPage.slugErrorNotification.isPresent();
                }).then(function (present) {
                    if (present === false) {
                        cmsProtractorHelper.waitFor(jobsPage.editPageLink);

                        // wait till the editPageLink will become clickable
                        browser.sleep(500);

                        // validate/click edit page link
                        jobsPage.editPageLink.click();

                        // switch to default page content
                        browser.switchTo().defaultContent();

                        cmsProtractorHelper.waitFor(jobsPage.testLink);

                        // validate test link text
                        jobsPage.testLink.getText().then(function (title) {
                            expect(title).toEqual('Test');
                        });
                    }
                });
            }
        });
    });

    it('creates a new apphook config', function () {
        // check if the focus is on sidebar ifarme
        jobsPage.editPageLink.isPresent().then(function (present) {
            if (present === false) {
                // wait for modal iframe to appear
                cmsProtractorHelper.waitFor(jobsPage.sideMenuIframe);

                // switch to sidebar menu iframe
                return browser.switchTo().frame(browser.findElement(By.css(
                    '.cms-sideframe-frame iframe')));
            }
        }).then(function () {
            cmsProtractorHelper.waitFor(jobsPage.breadcrumbsLinks.first());

            // click the Home link in breadcrumbs
            jobsPage.breadcrumbsLinks.first().click();

            cmsProtractorHelper.waitFor(jobsPage.jobsAddConfigsLink);

            jobsPage.jobsAddConfigsLink.click();

            cmsProtractorHelper.waitFor(jobsPage.namespaceInput);

            jobsPage.namespaceInput.sendKeys('aldryn_jobs').then(function () {
                jobsPage.saveButton.click();

                // check if Jobs configuration namespace already exists
                return jobsPage.namespaceErrorNotification.isPresent();
            }).then(function (present) {
                if (present === false) {
                    // wait for success notification
                    cmsProtractorHelper.waitFor(jobsPage.successNotification);

                    // validate success notification
                    expect(jobsPage.successNotification.isDisplayed())
                        .toBeTruthy();
                }
            });
        });
    });

    it('creates a new category', function () {
        cmsProtractorHelper.waitFor(jobsPage.breadcrumbsLinks.first());

        // click the Home link in breadcrumbs
        jobsPage.breadcrumbsLinks.first().click();

        cmsProtractorHelper.waitFor(jobsPage.jobsAddCategoriesLink);

        jobsPage.jobsAddCategoriesLink.click().then(function () {
            cmsProtractorHelper.waitFor(jobsPage.nameInput);

            return jobsPage.nameInput.sendKeys('Test category');
        }).then(function () {
            browser.actions().mouseMove(jobsPage.saveAndContinueButton)
                .perform();
            jobsPage.saveButton.click();

            // check if the category already exists and return the status
            return jobsPage.nameErrorNotification.isPresent();
        }).then(function (present) {
            if (present === false) {
                // wait for success notification
                cmsProtractorHelper.waitFor(jobsPage.successNotification);

                // validate success notification
                expect(jobsPage.successNotification.isDisplayed())
                    .toBeTruthy();
            }
        });
    });

    it('creates a new job opening', function () {
        cmsProtractorHelper.waitFor(jobsPage.breadcrumbsLinks.first());

        // click the Home link in breadcrumbs
        jobsPage.breadcrumbsLinks.first().click();

        cmsProtractorHelper.waitFor(jobsPage.addJobOpeningsButton);

        jobsPage.addJobOpeningsButton.click();

        cmsProtractorHelper.waitFor(jobsPage.titleInput);

        jobsPage.titleInput.sendKeys(jobName).then(function () {
            // set Category
            return cmsProtractorHelper.selectOption(jobsPage.categorySelect,
                'Jobs / aldryn_jobs / Test category', jobsPage.categoryOption);
        }).then(function () {
            // click Today link
            jobsPage.startDateLinks.first().click();
            // click Now link
            jobsPage.startTimeLinks.first().click();
            // set End date
            jobsPage.endDateInput.sendKeys('2100-07-09');
            // set End time
            return jobsPage.endTimeInput.sendKeys('12:34:56');
        }).then(function () {
            cmsProtractorHelper.waitFor(jobsPage.saveAndContinueButton);

            browser.actions().mouseMove(jobsPage.saveAndContinueButton)
                .perform();
            jobsPage.saveButton.click();

            cmsProtractorHelper.waitFor(jobsPage.successNotification);

            // validate success notification
            expect(jobsPage.successNotification.isDisplayed()).toBeTruthy();
            // validate edit job opening link
            expect(jobsPage.editJobOpeningLinks.first().isDisplayed())
                .toBeTruthy();
        });
    });

    it('adds a new jobs block on the page', function () {
        // switch to default page content
        browser.switchTo().defaultContent();

        cmsProtractorHelper.waitFor(jobsPage.testLink);

        // add jobs to the page only if it was not added before
        return jobsPage.aldrynJobsBlock.isPresent().then(function (present) {
            if (present === false) {
                // click the Page link in the top menu
                return jobsPage.userMenus.get(1).click().then(function () {
                    // wait for top menu dropdown options to appear
                    cmsProtractorHelper.waitFor(jobsPage.userMenuDropdown);

                    jobsPage.advancedSettingsOption.click();

                    // wait for modal iframe to appear
                    cmsProtractorHelper.waitFor(jobsPage.modalIframe);

                    // switch to modal iframe
                    browser.switchTo().frame(browser.findElement(By.css(
                        '.cms-modal-frame iframe')));

                    // set Jobs Application
                    cmsProtractorHelper.selectOption(jobsPage.applicationSelect,
                        'Jobs', jobsPage.jobsOption);

                    // switch to default page content
                    browser.switchTo().defaultContent();

                    cmsProtractorHelper.waitFor(jobsPage.saveModalButton);

                    browser.actions().mouseMove(jobsPage.saveModalButton)
                        .perform();
                    return jobsPage.saveModalButton.click();
                });
            }
        }).then(function () {
            cmsProtractorHelper.waitFor(jobsPage.testLink);

            // refresh the page to see changes
            browser.refresh();

            // wait for link to appear in aldryn jobs block
            cmsProtractorHelper.waitFor(jobsPage.jobsOpeningLink);

            jobsPage.jobsOpeningLink.click();

            cmsProtractorHelper.waitFor(jobsPage.jobTitle);

            // validate job title
            expect(jobsPage.jobTitle.isDisplayed()).toBeTruthy();
        });
    });

    it('deletes job opening', function () {
        // wait for modal iframe to appear
        cmsProtractorHelper.waitFor(jobsPage.sideMenuIframe);

        // switch to sidebar menu iframe
        browser.switchTo()
            .frame(browser.findElement(By.css('.cms-sideframe-frame iframe')));

        // wait for edit job opening link to appear
        cmsProtractorHelper.waitFor(jobsPage.editJobOpeningLinks.first());

        // validate edit job opening links texts to delete proper job opening
        jobsPage.editJobOpeningLinks.first().getText().then(function (text) {
            // wait till horizontal scrollbar will disappear and
            // editJobOpeningLinks will become clickable
            browser.sleep(1500);

            if (text === jobName) {
                return jobsPage.editJobOpeningLinks.first().click();
            } else {
                return jobsPage.editJobOpeningLinks.get(1).getText()
                    .then(function (text) {
                    if (text === jobName) {
                        return jobsPage.editJobOpeningLinks.get(1).click();
                    } else {
                        return jobsPage.editJobOpeningLinks.get(2).getText()
                            .then(function (text) {
                            if (text === jobName) {
                                return jobsPage.editJobOpeningLinks.get(2).click();
                            }
                        });
                    }
                });
            }
        }).then(function () {
            // wait for delete button to appear
            cmsProtractorHelper.waitFor(jobsPage.deleteButton);

            browser.actions().mouseMove(jobsPage.saveAndContinueButton)
                .perform();
            return jobsPage.deleteButton.click();
        }).then(function () {
            // wait for confirmation button to appear
            cmsProtractorHelper.waitFor(jobsPage.sidebarConfirmationButton);

            jobsPage.sidebarConfirmationButton.click();

            cmsProtractorHelper.waitFor(jobsPage.successNotification);

            // validate success notification
            expect(jobsPage.successNotification.isDisplayed()).toBeTruthy();

            // switch to default page content
            browser.switchTo().defaultContent();

            // refresh the page to see changes
            browser.refresh();
        });
    });

});
