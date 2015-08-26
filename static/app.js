var uberpy = angular.module('uberpy', ['ngRoute']);

uberpy.config(function($interpolateProvider, $routeProvider){
  $interpolateProvider.startSymbol('{[');
  $interpolateProvider.endSymbol(']}');

  $routeProvider
    .when('/', {
      templateUrl: '../static/partials/dashboard.html',
      controller: 'mainController'
    })
    .when('/reports', {
      templateUrl: '../static/partials/profile.html',
      controller: 'profileController'
    });

});

uberpy.controller('mainController', function($scope){
  $scope.message = "This is the main controller";
});

uberpy.controller('profileController', function($scope){
  $scope.message = 'This is the profile controller';
});
