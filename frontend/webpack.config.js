const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');

module.exports = {
  entry: './src/index.js',
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: 'bundle.js',
    publicPath: '/',
  },
  // Proxy to forward requests to the correct services and avoid CORS issues
  devServer: {
    static: {
      directory: path.join(__dirname, 'public'),
    },
    port: 3000,
    historyApiFallback: true,
    proxy: [
      {
        context: ['/api'], // Requests to '/api' go to service 1
        target: 'http://localhost:8001',
        changeOrigin: true,
      },
      {
        context: ['/api'], // Requests to '/auth' go to service 2
        target: 'http://localhost:8002',
        changeOrigin: true,
      },
    ],
    hot: true,
    allowedHosts: 'all', // Add this line to allow all hosts
  },
  plugins: [
    new HtmlWebpackPlugin({
      template: './public/index.html',
    }),
  ],
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/,
        exclude: /node_modules/,
        use: ['babel-loader'],
      },
    ],
  },
  resolve: {
    extensions: ['.js', '.jsx'],
  },
};