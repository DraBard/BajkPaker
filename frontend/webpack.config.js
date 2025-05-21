const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const webpack = require('webpack');

const HOST = process.env.HOST || '0.0.0.0';
const PORT = process.env.PORT || 3000;
const isDevelopment = process.env.NODE_ENV !== 'production';

module.exports = {
  mode: isDevelopment ? 'development' : 'production',
  entry: './src/index.js',
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: '[name].[contenthash].js',
    publicPath: '/',
    clean: true,
  },
  // Development server settings
  devServer: {
    host: HOST,
    port: PORT,
    static: {
      directory: path.join(__dirname, 'public'),
    },
    historyApiFallback: true,
    // Configure proxy only in development with improved settings
    ...(isDevelopment && {
      proxy: [
        {
          context: ['/api/bikes'],
          target: 'http://localhost:8001',
          pathRewrite: { '^/api': '' },
          secure: false,
          changeOrigin: true,
          onProxyReq: (proxyReq) => {
            // Log proxy requests for debugging
            console.log('Proxying request to bikes service:', proxyReq.path);
          },
          onError: (err, req, res) => {
            console.error('Proxy error:', err);
            res.writeHead(500, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ error: 'Proxy error', message: err.message }));
          },
        },
        {
          context: ['/api/cart', '/api/orders', '/api/payments'],
          target: 'http://localhost:8002',
          pathRewrite: { '^/api': '' },
          secure: false,
          changeOrigin: true,
          onProxyReq: (proxyReq) => {
            console.log('Proxying request to orders service:', proxyReq.path);
          },
        },
        {
          context: ['/api/users'],
          target: 'http://localhost:8003',
          pathRewrite: { '^/api': '' },
          secure: false,
          changeOrigin: true,
        },
      ],
    }),
    hot: true,
    allowedHosts: 'all',
  },
  plugins: [
    new HtmlWebpackPlugin({
      template: './public/index.html',
      // Removed favicon reference
    }),
    // Define environment variables
    new webpack.DefinePlugin({
      'process.env.NODE_ENV': JSON.stringify(process.env.NODE_ENV || 'development')
    }),
  ],
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/,
        exclude: /node_modules/,
        use: ['babel-loader'],
      },
      {
        test: /\.(png|svg|jpg|jpeg|gif|ico)$/i,
        type: 'asset/resource',
      },
    ],
  },
  resolve: {
    extensions: ['.js', '.jsx'],
  },
  // Add production optimizations
  optimization: {
    moduleIds: 'deterministic',
    runtimeChunk: 'single',
    splitChunks: {
      cacheGroups: {
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          chunks: 'all',
        },
      },
    },
  },
};