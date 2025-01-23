import React, { useState, useEffect } from 'react';
import { Box, TextField, Button, Typography, Paper, Table, TableBody, TableCell, TableHead, TableRow, Alert } from '@mui/material';
import { motion } from 'framer-motion';
import { Navigate } from 'react-router-dom';
import MachineStatus from './components/MachineStatus';

function Admin() {
  const [password, setPassword] = useState('');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [orders, setOrders] = useState([]);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [machineStatus, setMachineStatus] = useState(null);

  const handleLogin = () => {
    if (password === '2004') {
      setIsAuthenticated(true);
      setError('');
      fetchOrders();
      fetchMachineStatus();
    } else {
      setError('Invalid password');
    }
  };

  const fetchOrders = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/orders');
      const data = await response.json();
      setOrders(data);
    } catch (error) {
      setError('Failed to fetch orders');
    } finally {
      setIsLoading(false);
    }
  };

  const fetchMachineStatus = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/machine-status');
      const data = await response.json();
      setMachineStatus(data);
    } catch (error) {
      setError('Failed to fetch machine status');
    }
  };

  useEffect(() => {
    if (isAuthenticated) {
      fetchOrders();
      fetchMachineStatus();
      // Poll for updates every 5 seconds
      const interval = setInterval(() => {
        fetchMachineStatus();
      }, 5000);
      return () => clearInterval(interval);
    }
  }, [isAuthenticated]);

  if (!isAuthenticated) {
    return (
      <Box sx={{ p: 4, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <Typography variant="h4" sx={{ mb: 4, color: '#4CAF50' }}>
          Admin Login
        </Typography>
        <Box sx={{ width: '100%', maxWidth: 400 }}>
          <TextField
            fullWidth
            type="password"
            label="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleLogin()}
            sx={{ mb: 2 }}
          />
          <Button
            fullWidth
            variant="contained"
            color="primary"
            onClick={handleLogin}
            sx={{ mb: 2 }}
          >
            Login
          </Button>
          {error && <Alert severity="error">{error}</Alert>}
        </Box>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 4 }}>
      <Typography variant="h4" sx={{ mb: 4, color: '#4CAF50' }}>
        Vending Machine Dashboard
      </Typography>
      
      {machineStatus && <MachineStatus status={machineStatus} />}

      <Typography variant="h5" sx={{ mb: 3 }}>
        Order History
      </Typography>
      {isLoading ? (
        <Typography>Loading orders...</Typography>
      ) : (
        <Paper sx={{ overflow: 'auto' }}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Time</TableCell>
                <TableCell>Cup Type</TableCell>
                <TableCell>Flavor</TableCell>
                <TableCell>Water Quantity</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {orders.map((order, index) => (
                <TableRow key={index}>
                  <TableCell>{new Date(order.timestamp).toLocaleString()}</TableCell>
                  <TableCell>{order.cup_type}</TableCell>
                  <TableCell>{order.flavor}</TableCell>
                  <TableCell>{order.water_quantity}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Paper>
      )}
    </Box>
  );
}

export default Admin;
