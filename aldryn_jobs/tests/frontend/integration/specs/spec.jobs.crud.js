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
    // create random job name
    var jobName = 'Test job ' + (Math.floor(Math.random() * 10001));

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

    it('creates a new apphook config', function () {
        // check if the focus is on sidebar ifarme
        jobsPage.editPageLink.isPresent().then(function (present) {
            if (present === false) {
                // wait for modal iframe to appear
                browser.wait(function () {
                    return browser.isElementPresent(jobsPage.sideMenuIframe);
                }, jobsPage.iframeWaitTime);

                // switch to sidebar menu iframe
                return browser.switchTo().frame(browser.findElement(By.css(
                    '.cms_sideframe-frame iframe')));
            }
        }).then(function () {
            browser.wait(function () {
                return browser.isElementPresent(jobsPage.breadcrumbsLinks.first());
            }, jobsPage.mainElementsWaitTime);

            // click the Home link in breadcrumbs
            jobsPage.breadcrumbsLinks.first().click();

            browser.wait(function () {
                return browser.isElementPresent(jobsPage.jobsAddConfigsLink);
            }, jobsPage.mainElementsWaitTime);

            jobsPage.jobsAddConfigsLink.click();

            browser.wait(function () {
                return browser.isElementPresent(jobsPage.namespaceInput);
            }, jobsPage.mainElementsWaitTime);

            jobsPage.namespaceInput.sendKeys('aldryn_jobs').then(function () {
                jobsPage.saveButton.click();

                // check if Jobs configuration namespace already exists
                return jobsPage.namespaceErrorNotification.isPresent();
            }).then(function (present) {
                if (present === false) {
                    // wait for success notification
                    browser.wait(function () {
                        return browser.isElementPresent(jobsPage.successNotification);
                    }, jobsPage.mainElementsWaitTime);

                    // validate success notification
                    expect(jobsPage.successNotification.isDisplayed())
                        .toBeTruthy();
                }
            });
        });
    });

    it('creates a new category', function () {
        browser.wait(function () {
            return browser.isElementPresent(jobsPage.breadcrumbsLinks.first());
        }, jobsPage.mainElementsWaitTime);

        // click the Home link in breadcrumbs
        jobsPage.breadcrumbsLinks.first().click();

        browser.wait(function () {
            return browser.isElementPresent(jobsPage.jobsAddCategoriesLink);
        }, jobsPage.mainElementsWaitTime);

        jobsPage.jobsAddCategoriesLink.click().then(function () {
            browser.wait(function () {
                return browser.isElementPresent(jobsPage.nameInput);
            }, jobsPage.mainElementsWaitTime);

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
                browser.wait(function () {
                    return browser.isElementPresent(jobsPage.successNotification);
                }, jobsPage.mainElementsWaitTime);

                // validate success notification
                expect(jobsPage.successNotification.isDisplayed())
                    .toBeTruthy();
            }
        });
    });

    it('creates a new job opening', function () {
        browser.wait(function () {
            return browser.isElementPresent(jobsPage.breadcrumbsLinks.first());
        }, jobsPage.mainElementsWaitTime);

        // click the Home link in breadcrumbs
        jobsPage.breadcrumbsLinks.first().click();

        browser.wait(function () {
            return browser.isElementPresent(jobsPage.addJobOpeningsButton);
        }, jobsPage.mainElementsWaitTime);

        jobsPage.addJobOpeningsButton.click();

        browser.wait(function () {
            return browser.isElementPresent(jobsPage.titleInput);
        }, jobsPage.mainElementsWaitTime);

        jobsPage.titleInput.sendKeys(jobName).then(function () {
            // set Category
            jobsPage.categorySelect.click();

            return jobsPage.categorySelect.sendKeys('Jobs / aldryn_jobs / Test category');
        }).then(function () {
            return jobsPage.categorySelect.click();
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
            browser.wait(function () {
                return browser.isElementPresent(jobsPage.saveAndContinueButton);
            }, jobsPage.mainElementsWaitTime);

            browser.actions().mouseMove(jobsPage.saveAndContinueButton)
                .perform();
            jobsPage.saveButton.click();

            browser.wait(function () {
                return browser.isElementPresent(jobsPage.successNotification);
            }, jobsPage.mainElementsWaitTime);

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

        browser.wait(function () {
            return browser.isElementPresent(jobsPage.testLink);
        }, jobsPage.mainElementsWaitTime);

        // add jobs to the page only if it was not added before
        jobsPage.aldrynJobsBlock.isPresent().then(function (present) {
            if (present === false) {
                // click the Page link in the top menu
                return jobsPage.userMenus.get(1).click().then(function () {
                    // wait for top menu dropdown options to appear
                    browser.wait(function () {
                        return browser.isElementPresent(jobsPage.userMenuDropdown);
                    }, jobsPage.mainElementsWaitTime);

                    jobsPage.advancedSettingsOption.click();

                    // wait for modal iframe to appear
                    browser.wait(function () {
                        return browser.isElementPresent(jobsPage.modalIframe);
                    }, jobsPage.iframeWaitTime);

                    // switch to modal iframe
                    browser.switchTo().frame(browser.findElement(By.css(
                        '.cms_modal-frame iframe')));

                    // wait for Application select to appear
                    browser.wait(function () {
                        return browser.isElementPresent(jobsPage.applicationSelect);
                    }, jobsPage.mainElementsWaitTime);

                    // set Application
                    jobsPage.applicationSelect.click();
                    jobsPage.applicationSelect.sendKeys('Jobs')
                        .then(function () {
                        jobsPage.applicationSelect.click();
                    });

                    // switch to default page content
                    browser.switchTo().defaultContent();

                    browser.wait(function () {
                        return browser.isElementPresent(jobsPage.saveModalButton);
                    }, jobsPage.mainElementsWaitTime);

                    browser.actions().mouseMove(jobsPage.saveModalButton)
                        .perform();
                    return jobsPage.saveModalButton.click();
                });
            }
        }).then(function () {
            // refresh the page to see changes
            browser.refresh();

            // wait for link to appear in aldryn jobs block
            browser.wait(function () {
                return browser.isElementPresent(jobsPage.jobsOpeningLink);
            }, jobsPage.mainElementsWaitTime);

            jobsPage.jobsOpeningLink.click();

            browser.wait(function () {
                return browser.isElementPresent(jobsPage.jobTitle);
            }, jobsPage.mainElementsWaitTime);

            // validate job title
            expect(jobsPage.jobTitle.isDisplayed()).toBeTruthy();
        });
    });

    it('deletes job opening', function () {
        // wait for modal iframe to appear
        browser.wait(function () {
            return browser.isElementPresent(jobsPage.sideMenuIframe);
        }, jobsPage.iframeWaitTime);

        // switch to sidebar menu iframe
        browser.switchTo()
            .frame(browser.findElement(By.css('.cms_sideframe-frame iframe')));

        // wait for edit job opening link to appear
        browser.wait(function () {
            return browser.isElementPresent(jobsPage.editJobOpeningLinks.first());
        }, jobsPage.mainElementsWaitTime);

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
                        jobsPage.editJobOpeningLinks.get(1).click();
                    } else {
                        return jobsPage.editJobOpeningLinks.get(2).getText()
                            .then(function (text) {
                            if (text === jobName) {
                                jobsPage.editJobOpeningLinks.get(2).click();
                            }
                        });
                    }
                });
            }
        }).then(function () {
            // wait for delete button to appear
            browser.wait(function () {
                return browser.isElementPresent(jobsPage.deleteButton);
            }, jobsPage.mainElementsWaitTime);

            browser.actions().mouseMove(jobsPage.saveAndContinueButton)
                .perform();
            return jobsPage.deleteButton.click();
        }).then(function () {
            // wait for confirmation button to appear
            browser.wait(function () {
                return browser.isElementPresent(jobsPage.sidebarConfirmationButton);
            }, jobsPage.mainElementsWaitTime);

            jobsPage.sidebarConfirmationButton.click();

            browser.wait(function () {
                return browser.isElementPresent(jobsPage.successNotification);
            }, jobsPage.mainElementsWaitTime);

            // validate success notification
            expect(jobsPage.successNotification.isDisplayed()).toBeTruthy();

            // switch to default page content
            browser.switchTo().defaultContent();

            // refresh the page to see changes
            browser.refresh();
        });
    });

});
