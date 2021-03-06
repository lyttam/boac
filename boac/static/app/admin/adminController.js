/**
 * Copyright ©2018. The Regents of the University of California (Regents). All Rights Reserved.
 *
 * Permission to use, copy, modify, and distribute this software and its documentation
 * for educational, research, and not-for-profit purposes, without fee and without a
 * signed licensing agreement, is hereby granted, provided that the above copyright
 * notice, this paragraph and the following two paragraphs appear in all copies,
 * modifications, and distributions.
 *
 * Contact The Office of Technology Licensing, UC Berkeley, 2150 Shattuck Avenue,
 * Suite 510, Berkeley, CA 94720-1620, (510) 643-7201, otl@berkeley.edu,
 * http://ipira.berkeley.edu/industry-info for commercial licensing opportunities.
 *
 * IN NO EVENT SHALL REGENTS BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT, SPECIAL,
 * INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING LOST PROFITS, ARISING OUT OF
 * THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF REGENTS HAS BEEN ADVISED
 * OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 * REGENTS SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. THE
 * SOFTWARE AND ACCOMPANYING DOCUMENTATION, IF ANY, PROVIDED HEREUNDER IS PROVIDED
 * "AS IS". REGENTS HAS NO OBLIGATION TO PROVIDE MAINTENANCE, SUPPORT, UPDATES,
 * ENHANCEMENTS, OR MODIFICATIONS.
 */

(function(angular) {

  'use strict';

  angular.module('boac').controller('AdminController', function(
    $location,
    $scope,
    adminFactory,
    config,
    page,
    userFactory
  ) {

    $scope.demoMode = config.demoMode.blur;

    $scope.become = function(uid) {
      adminFactory.becomeUser(uid).then(function() {
        window.location = '/';
      });
    };

    $scope.toggleDemoMode = function() {
      $scope.isToggling = true;
      var blur = !$scope.demoMode;

      adminFactory.setDemoMode(blur).then(function(response) {
        $scope.demoMode = response.data.blur;
        $scope.isToggling = false;
      });
    };

    var getDeptName = function(deptCode) {
      switch (deptCode) {
        case 'COENG': return 'College of Engineering';
        case 'UWASC': return 'Athletic Study Center';
        default: return null;
      }
    };

    var groupByDept = function(advisors) {
      var byDept = _.groupBy(advisors, function(advisor) {
        var deptCodes = _.keys(advisor.departments);
        return deptCodes.length ? deptCodes[0] : null;
      });
      var groups = _.map(byDept, function(users, deptCode) {
        return {
          name: getDeptName(deptCode),
          userCount: users.length,
          users: users
        };
      });
      return _.sortBy(groups, 'name');
    };

    var init = function() {
      page.loading(true);
      if (config.devAuthEnabled) {
        userFactory.getAllUserProfiles().then(function(response) {
          var byIsAdmin = _.groupBy(response.data, 'is_admin');
          var adminUsers = byIsAdmin.true;

          $scope.groups = [
            {
              name: 'Admins',
              userCount: adminUsers.length,
              users: adminUsers
            }
          ].concat(groupByDept(byIsAdmin.false));

          page.loading(false);
        });
      } else {
        $location.replace().path('/404');
      }
    };

    init();
  });

}(window.angular));
