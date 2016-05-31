'use strict';

var helpers = require('djangocms-casper-helpers');
var globals = helpers.settings;
var casperjs = require('casper');
var cms = helpers(casperjs);
var xPath = casperjs.selectXPath;

casper.test.setUp(function (done) {
    casper.start()
        .then(cms.login())
        .run(done);
});

casper.test.tearDown(function (done) {
    casper.start()
        .then(cms.logout())
        .run(done);
});

casper.test.begin('Creation / deletion of the apphook', function (test) {
    casper
        .start(globals.adminUrl)
        .waitUntilVisible('#content', function () {
            test.assertVisible('#content', 'Admin loaded');
            this.click(
                xPath(cms.getXPathForAdminSection({
                    section: 'Aldryn Jobs',
                    row: 'Aldryn Jobs configurations',
                    link: 'Add'
                }))
            );
        })
        .waitForUrl(/add/)
        .waitUntilVisible('#jobsconfig_form')
        .then(function () {
            test.assertVisible('#jobsconfig_form', 'Apphook creation form loaded');

            this.fill('#jobsconfig_form', {
                namespace: 'Test namespace'
            }, true);
        })
        .waitUntilVisible('.success', function () {
            test.assertSelectorHasText(
                '.success',
                'The Aldryn Jobs configuration "Jobs / Test namespace" was added successfully.',
                'Apphook config has been created'
            );

            test.assertElementCount(
                '#result_list tbody tr',
                2,
                'There are 2 apphooks now'
            );

            this.clickLabel('Jobs / Test namespace', 'a');
        })
        .waitUntilVisible('.deletelink', function () {
            this.click('.deletelink');
        })
        .waitForUrl(/delete/, function () {
            this.click('input[value="Yes, I\'m sure"]');
        })
        .waitUntilVisible('.success', function () {
            test.assertSelectorHasText(
                '.success',
                'The Aldryn Jobs configuration "Jobs / Test namespace" was deleted successfully.',
                'Apphook config has been deleted'
            );
        })
        .run(function () {
            test.done();
        });
});

casper.test.begin('Creation of a new jobs category', function (test) {
    casper
        .start(globals.adminUrl)
        .waitUntilVisible('#content', function () {
            this.click(
                xPath(cms.getXPathForAdminSection({
                    section: 'Aldryn Jobs',
                    row: 'Job categories',
                    link: 'Add'
                }))
            );
        })
        .waitForUrl(/add/)
        .waitUntilVisible('#jobcategory_form')
        .then(function () {
            test.assertVisible('#jobcategory_form', 'Jobs category creation form has been loaded');

            this.fill('#jobcategory_form', {
                name: 'Test category'
            }, true);
        })
        .waitUntilVisible('.success', function () {
            test.assertSelectorHasText(
                '.success',
                'The job category "Test category" was added successfully.',
                'New jobs category has been created'
            );
        })
        .run(function () {
            test.done();
        });
});

casper.test.begin('Creation of a new job opening', function (test) {
    casper
        .start(globals.adminUrl)
        .waitUntilVisible('#content', function () {
            this.click(
                xPath(cms.getXPathForAdminSection({
                    section: 'Aldryn Jobs',
                    row: 'Job openings',
                    link: 'Add'
                }))
            );
        })
        .waitForUrl(/add/)
        .waitUntilVisible('#jobopening_form')
        .then(function () {
            test.assertVisible('#jobopening_form', 'Job opening creation form has been loaded');

            this.fill('#jobopening_form', {
                title: 'Test job',
                category: 'Jobs / aldryn_jobs / Test category'
            }, true);
        })
        .waitUntilVisible('.success', function () {
            test.assertSelectorHasText(
                '.success',
                'The job opening "Test job" was added successfully.',
                'New job opening has been created'
            );
        })
        .run(function () {
            test.done();
        });
});

casper.test.begin('Adding a new jobs block to the page', function (test) {
    casper
        .start()
        .then(cms.addPage({ title: 'Jobs' }))
        .then(cms.addApphookToPage({
            page: 'Jobs',
            apphook: 'JobsApp'
        }))
        .then(cms.publishPage({
            page: 'Jobs'
        }))
        .thenOpen(globals.editUrl, function () {
            test.assertTitleMatch(/Jobs/, 'The Jobs page has been created');

            test.assertSelectorHasText(
                'p',
                'Test category',
                'The "Test category" link is available'
            );

            test.assertSelectorHasText(
                'h3 a',
                'Test job',
                'The "Test job" link is available'
            );
        })
        .run(function () {
            test.done();
        });
});

casper.test.begin('Deletion of a job opening', function (test) {
    casper
        .start(globals.adminUrl)
        .waitUntilVisible('#content', function () {
            this.click(
                xPath(cms.getXPathForAdminSection({
                    section: 'Aldryn Jobs',
                    row: 'Job openings',
                    link: 'Change'
                }))
            );
        })
        .waitForUrl(/jobopening/)
        .waitUntilVisible('#result_list', function () {
            test.assertElementCount(
                '#result_list tbody tr',
                1,
                'The job is available'
            );

            this.clickLabel('Test job', 'a');
        })
        .waitUntilVisible('.deletelink', function () {
            this.click('.deletelink');
        })
        .waitForUrl(/delete/, function () {
            this.click('input[value="Yes, I\'m sure"]');
        })
        .waitUntilVisible('.success', function () {
            test.assertSelectorHasText(
                '.success',
                'The job opening "Test job" was deleted successfully.',
                'The job opening has been deleted'
            );
        })
        .run(function () {
            test.done();
        });
});

casper.test.begin('Deletion of a job category', function (test) {
    casper
        .start(globals.adminUrl)
        .waitUntilVisible('#content', function () {
            this.click(
                xPath(cms.getXPathForAdminSection({
                    section: 'Aldryn Jobs',
                    row: 'Job categories',
                    link: 'Change'
                }))
            );
        })
        .waitForUrl(/jobcategory/)
        .waitUntilVisible('#result_list', function () {
            test.assertElementCount(
                '#result_list tbody tr',
                1,
                'The job category is available'
            );

            this.clickLabel('Test category', 'a');
        })
        .waitUntilVisible('.deletelink', function () {
            this.click('.deletelink');
        })
        .waitForUrl(/delete/, function () {
            this.click('input[value="Yes, I\'m sure"]');
        })
        .waitUntilVisible('.success', function () {
            test.assertSelectorHasText(
                '.success',
                'The job category "Test category" was deleted successfully.',
                'The job category has been deleted'
            );
        })
        .run(function () {
            test.done();
        });
});
