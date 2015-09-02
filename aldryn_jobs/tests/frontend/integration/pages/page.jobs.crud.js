/*!
 * @author:    Divio AG
 * @copyright: http://www.divio.ch
 */

'use strict';
/* global element, by, browser, expect */

// #############################################################################
// INTEGRATION TEST PAGE OBJECT

var jobsPage = {
    site: 'http://127.0.0.1:8000/en/',
    mainElementsWaitTime: 12000,
    iframeWaitTime: 15000,

    // log in
    editModeLink: element(by.css('.inner a[href="/?edit"]')),
    usernameInput: element(by.id('id_cms-username')),
    passwordInput: element(by.id('id_cms-password')),
    loginButton: element(by.css('.cms_form-login input[type="submit"]')),
    userMenus: element.all(by.css('.cms_toolbar-item-navigation > li > a')),
    testLink: element(by.css('.selected a')),

    // adding new page
    userMenuDropdown: element(by.css(
        '.cms_toolbar-item-navigation-hover')),
    administrationOptions: element.all(by.css(
        '.cms_toolbar-item-navigation a[href="/en/admin/"]')),
    sideMenuIframe: element(by.css('.cms_sideframe-frame iframe')),
    pagesLink: element(by.css('.model-page > th > a')),
    addConfigsButton: element(by.css('.object-tools .addlink')),
    addPageLink: element(by.css('.sitemap-noentry .addlink')),
    titleInput: element(by.id('id_title')),
    slugErrorNotification: element(by.css('.errors.slug')),
    saveButton: element(by.css('.submit-row [name="_save"]')),
    editPageLink: element(by.css('.col1 [href*="preview/"]')),

    // adding new apphook config
    breadcrumbsLinks: element.all(by.css('.breadcrumbs a')),
    jobsAddConfigsLink: element(by.css('.model-jobsconfig .addlink')),
    namespaceInput: element(by.id('id_namespace')),
    namespaceErrorNotification: element(by.css('.errors.field-namespace')),
    successNotification: element(by.css('.messagelist .success')),

    // adding new category
    jobsAddCategoriesLink: element(by.css('.model-jobcategory .addlink')),
    nameInput: element(by.id('id_name')),
    saveAndContinueButton: element(by.css('.submit-row [name="_continue"]')),
    nameErrorNotification: element(by.css('.errors.field-name')),

    // adding new job opening
    addJobOpeningsButton: element(by.css('.model-jobopening .addlink')),
    categorySelect: element(by.id('id_category')),
    categoryOption: element(by.css('#id_category > option:nth-child(2)')),
    startDateLinks: element.all(by.css(
        '#id_publication_start_0 + .datetimeshortcuts > a')),
    startTimeLinks: element.all(by.css(
        '#id_publication_start_1 + .datetimeshortcuts > a')),
    endDateInput: element(by.id('id_publication_end_0')),
    endTimeInput: element(by.id('id_publication_end_1')),
    editJobOpeningLinks: element.all(by.css(
        '.results th > [href*="/aldryn_jobs/jobopening/"]')),

    // adding jobs block to the page
    aldrynJobsBlock: element(by.css('.app-jobs')),
    advancedSettingsOption: element(by.css(
        '.cms_toolbar-item-navigation [href*="advanced-settings"]')),
    modalIframe: element(by.css('.cms_modal-frame iframe')),
    applicationSelect: element(by.id('application_urls')),
    jobsOption: element(by.css('option[value="JobsApp"]')),
    saveModalButton: element(by.css('.cms_modal-buttons .cms_btn-action')),
    jobsOpeningLink: element(by.css('.jobs-title > a')),
    jobTitle: element(by.css('.jobs-detail h2 > div')),

    // deleting job opening
    deleteButton: element(by.css('.deletelink-box a')),
    sidebarConfirmationButton: element(by.css('#content [type="submit"]')),

    cmsLogin: function (credentials) {
        // object can contain username and password, if not set it will
        // fallback to 'admin'
        credentials = credentials ||
            { username: 'admin', password: 'admin' };

        jobsPage.usernameInput.clear();

        // fill in email field
        jobsPage.usernameInput.sendKeys(
            credentials.username).then(function () {
            jobsPage.passwordInput.clear();

            // fill in password field
            return jobsPage.passwordInput.sendKeys(
                credentials.password);
        }).then(function () {
            jobsPage.loginButton.click();

            // wait for user menu to appear
            browser.wait(browser.isElementPresent(
                jobsPage.userMenus.first()),
                jobsPage.mainElementsWaitTime);

            // validate user menu
            expect(jobsPage.userMenus.first().isDisplayed())
                .toBeTruthy();
        });
    }

};

module.exports = jobsPage;
