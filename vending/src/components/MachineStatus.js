import React from 'react';
import { Box, Paper, Grid, Typography, LinearProgress } from '@mui/material';
import { motion } from 'framer-motion';

const MachineStatus = ({ status }) => {
  const flavorColors = {
    cola: '#663300',
    orange: '#FFA500',
    lemon: '#FFFF00',
    grape: '#800080',
    water: '#00FFFF',
    coffee: '#4B3621',
    tea: '#967969',
    energy: '#FF0000',
    sprite: '#90EE90'
  };

  return (
    <Paper sx={{ p: 3, mb: 3 }}>
      <Typography variant="h6" sx={{ mb: 2 }}>Machine Status</Typography>
      
      {/* Water Level */}
      <Box sx={{ mb: 3 }}>
        <Typography>Water Level</Typography>
        <LinearProgress 
          variant="determinate" 
          value={status.waterLevel} 
          sx={{ height: 20, borderRadius: 1 }}
        />
        <Typography variant="caption">{status.waterLevel}%</Typography>
      </Box>

      {/* Cup Balance */}
      <Box sx={{ mb: 3 }}>
        <Typography>Cups Remaining</Typography>
        <motion.div
          animate={{ rotate: status.isDispensing ? 360 : 0 }}
          transition={{ duration: 1, repeat: status.isDispensing ? Infinity : 0 }}
        >
          <Typography variant="h4">{status.cupsBalance}</Typography>
        </motion.div>
      </Box>

      {/* Blender Status */}
      <Box sx={{ mb: 3 }}>
        <Typography>
          Blender Status: 
          <motion.span
            animate={{ scale: status.blenderActive ? [1, 1.2, 1] : 1 }}
            transition={{ duration: 0.5, repeat: status.blenderActive ? Infinity : 0 }}
            style={{ color: status.blenderActive ? 'green' : 'grey' }}
          >
            ● {status.blenderActive ? 'Active' : 'Idle'}
          </motion.span>
        </Typography>
      </Box>

      {/* Flavor Quantities */}
      <Grid container spacing={2}>
        {Object.entries(status.flavors).map(([flavor, quantity]) => (
          <Grid item xs={4} key={flavor}>
            <Box sx={{ mb: 1 }}>
              <Typography variant="caption">{flavor}</Typography>
              <LinearProgress 
                variant="determinate" 
                value={(quantity / 1000) * 100}
                sx={{ 
                  height: 15, 
                  borderRadius: 1,
                  '& .MuiLinearProgress-bar': {
                    backgroundColor: flavorColors[flavor.toLowerCase()]
                  }
                }}
              />
              <Typography variant="caption">{quantity}ml</Typography>
            </Box>
          </Grid>
        ))}
      </Grid>
    </Paper>
  );
};

export default MachineStatus;
