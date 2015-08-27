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
    });

});

uberpy.controller('mainController', function($scope){
  $scope.message = "This is the main controller";
});

uberpy.controller('productsController', function($scope, $http){
  $http.get('/products')
    .success(function(data, code){
      $scope.products = data.products;
    })
    .error(function(data, code){
      console.log(data);
      console.log(code);
    });
  $scope.message = 'This is the profile controller';
});
