var uberpy = angular.module('uberpy', ['ngRoute']);

uberpy.config(function($interpolateProvider, $routeProvider){
  $interpolateProvider.startSymbol('{[');
  $interpolateProvider.endSymbol(']}');

  $routeProvider
    .when('/', {
      templateUrl: '../static/partials/dashboard.html',
      controller: 'mainController'
    })
    .when('/products', {
      templateUrl: '../static/partials/products.html',
      controller: 'productsController'
    })
    .when('/simulate', {
      templateUrl: '../static/partials/simulate.html',
      controller: 'simulatorController'
    });

});

uberpy.controller('mainController', function($scope){
  $scope.message = "This is the main controller";
});

uberpy.controller('productsController', function($scope, $http){
  $http.get('/products.json')
    .success(function(data, code){
      $scope.products = data.products;
    })
    .error(function(data, code){
      console.log(data);
      console.log(code);
    });
  $scope.message = 'This is the profile controller';
});

uberpy.controller('simulatorController', function($scope, $http){
  $scope.message = "This is the simulator";
  $('#simulate-btn').on('click', function(){
    $http.get('/simulate.json')
      .success(function(data, code){
        console.log(data);
      })
      .error(function(data, code){
        console.log(data);
      });
  });
});
