import React, { useState } from 'react';
import { Box, Stepper, Step, StepLabel, Button, Paper, Typography, CircularProgress, Alert, Snackbar } from '@mui/material';
import { motion, AnimatePresence } from 'framer-motion';

function App() {
    const [activeStep, setActiveStep] = useState(0);
    const [cupType, setCupType] = useState('');
    const [flavor, setFlavor] = useState('');
    const [waterQuantity, setWaterQuantity] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [notification, setNotification] = useState({ open: false, message: '', severity: 'success' });

    const steps = ['Select Cup Type', 'Choose Flavor', 'Set Water Quantity'];

    const handleClose = () => {
        setNotification({ ...notification, open: false });
    };

    const handleNext = async () => {
        if (activeStep === steps.length - 1) {
            setIsLoading(true);
            try {
                const response = await fetch('http://localhost:8000/api/process-order', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        cupType,
                        flavor,
                        waterQuantity
                    })
                });

                let data;
                try {
                    data = await response.json();
                } catch (parseError) {
                    throw new Error('Invalid JSON response from server');
                }

                if (!response.ok) {
                    throw new Error(data.detail || 'Failed to process order');
                }

                setNotification({
                    open: true,
                    message: `${data.message} - ${data.order_details.cup_type} cup with ${data.order_details.flavor}, ${data.order_details.water_quantity}ml`,
                    severity: 'success'
                });

                // Reset the form
                setCupType('');
                setFlavor('');
                setWaterQuantity('');
                setActiveStep(0);
            } catch (error) {
                setNotification({
                    open: true,
                    message: error.message,
                    severity: 'error'
                });
            } finally {
                setIsLoading(false);
            }
        } else {
            setActiveStep((prevStep) => prevStep + 1);
        }
    };

    const handleBack = () => {
        setActiveStep((prevStep) => prevStep - 1);
    };

    const theme = {
        primary: '#4CAF50',
        light: '#81C784',
        dark: '#388E3C',
        background: 'linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%)',
        section: '#FFFFFF',
        accent: '#66BB6A'
    };

    const containerStyle = {
        width: '90%',
        maxWidth: '1000px',
        minHeight: '700px',
        position: 'relative',
        overflow: 'hidden',
        backgroundColor: theme.section,
        borderRadius: '24px',
        boxShadow: '0 8px 32px rgba(0,0,0,0.12)',
        border: '1px solid rgba(76, 175, 80, 0.1)',
    };

    const sectionStyle = {
        padding: '32px',
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
    };

    const buttonStyle = {
        width: '100%',
        height: '70px',
        margin: '8px 0',
        borderRadius: '16px',
        textTransform: 'none',
        fontSize: '1.2rem',
        fontWeight: '500',
        borderColor: theme.primary,
        transition: 'all 0.4s ease',
        boxShadow: '0 4px 12px rgba(0,0,0,0.05)',
        '&.MuiButton-contained': {
            backgroundColor: theme.primary,
            '&:hover': {
                backgroundColor: theme.dark,
                transform: 'translateY(-3px)',
                boxShadow: '0 6px 16px rgba(0,0,0,0.15)',
            }
        },
        '&.MuiButton-outlined': {
            color: theme.primary,
            borderWidth: '2px',
            '&:hover': {
                backgroundColor: 'rgba(76, 175, 80, 0.08)',
                borderColor: theme.dark,
                transform: 'translateY(-3px)',
                boxShadow: '0 6px 16px rgba(0,0,0,0.15)',
            }
        }
    };

    const LoadingOverlay = () => (
        <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            style={{
                position: 'absolute',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                backgroundColor: 'rgba(255,255,255,0.9)',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                zIndex: 1000,
            }}
        >
            <CircularProgress size={60} sx={{ color: theme.primary }} />
            <Typography variant="h6" sx={{ mt: 2, color: theme.primary }}>
                Processing your selection...
            </Typography>
        </motion.div>
    );

    const getStepContent = (step) => {
        return (
            <AnimatePresence mode='wait'>
                <motion.div
                    key={step}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    transition={{ duration: 0.4 }}
                    style={{ width: '100%', maxWidth: '800px', margin: '0 auto' }}
                >
                    <section style={{ padding: '20px' }}>
                        {step === 0 && (
                            <Box sx={{ display: 'grid', gap: 3, maxWidth: '600px', margin: '0 auto' }}>
                                <Typography variant="h6" sx={{ color: theme.primary, mb: 2, textAlign: 'center' }}>
                                    Please select your cup preference
                                </Typography>
                                <Button variant={cupType === 'user' ? 'contained' : 'outlined'}
                                    onClick={() => setCupType('user')}
                                    sx={buttonStyle}>
                                    User Cup
                                </Button>
                                <Button variant={cupType === 'machine' ? 'contained' : 'outlined'}
                                    onClick={() => setCupType('machine')}
                                    sx={buttonStyle}>
                                    Machine Cup
                                </Button>
                            </Box>
                        )}
                        {step === 1 && (
                            <Box>
                                <Typography variant="h6" sx={{ color: theme.primary, mb: 3, textAlign: 'center' }}>
                                    Choose your favorite flavor
                                </Typography>
                                <Box sx={{
                                    display: 'grid',
                                    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                                    gap: 3,
                                    maxWidth: '800px',
                                    margin: '0 auto'
                                }}>
                                    {[1, 2, 3, 4, 5, 6, 7, 8, 9].map((flavorNumber) => (
                                        <Button key={flavorNumber}
                                            variant={flavor === flavorNumber.toString() ? 'contained' : 'outlined'}
                                            onClick={() => setFlavor(flavorNumber.toString())}
                                            sx={buttonStyle}>
                                            Flavor {flavorNumber}
                                        </Button>
                                    ))}
                                </Box>
                            </Box>
                        )}

                        {step === 2 && (
                            <Box sx={{ display: 'grid', gap: 3, maxWidth: '600px', margin: '0 auto' }}>
                                <Typography variant="h6" sx={{ color: theme.primary, mb: 2, textAlign: 'center' }}>
                                    Select water quantity
                                </Typography>
                                <Button variant={waterQuantity === '200' ? 'contained' : 'outlined'}
                                    onClick={() => setWaterQuantity('200')}
                                    sx={buttonStyle}>
                                    200 ml
                                </Button>
                                <Button variant={waterQuantity === '400' ? 'contained' : 'outlined'}
                                    onClick={() => setWaterQuantity('400')}
                                    sx={buttonStyle}>
                                    400 ml
                                </Button>
                            </Box>
                        )}
                    </section>
                </motion.div>
            </AnimatePresence>
        );
    };

    return (
        <div style={{
            minHeight: '100vh',
            background: theme.background,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '40px 20px'
        }}>
            <Snackbar
                open={notification.open}
                autoHideDuration={6000}
                onClose={handleClose}
                anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
            >
                <Alert
                    onClose={handleClose}
                    severity={notification.severity}
                    sx={{ width: '100%', boxShadow: '0 4px 12px rgba(0,0,0,0.15)' }}
                >
                    {notification.message}
                </Alert>
            </Snackbar>
            <motion.div
                style={containerStyle}
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5 }}
            >
                <Box sx={sectionStyle}>
                    <motion.div
                        initial={{ y: -20 }}
                        animate={{ y: 0 }}
                        transition={{ duration: 0.5 }}
                    >
                        <Typography variant="h3"
                            sx={{
                                color: theme.primary,
                                fontWeight: 'bold',
                                mb: 4,
                                textAlign: 'center',
                                position: 'relative',
                                '&::after': {
                                    content: '""',
                                    position: 'absolute',
                                    bottom: '-10px',
                                    left: '50%',
                                    transform: 'translateX(-50%)',
                                    width: '60px',
                                    height: '4px',
                                    backgroundColor: theme.primary,
                                    borderRadius: '2px'
                                }
                            }}>
                            Vending Machine
                        </Typography>
                    </motion.div>

                    <Stepper activeStep={activeStep}
                        sx={{
                            width: '100%',
                            maxWidth: '800px',
                            padding: '20px 0 40px',
                            '& .MuiStepLabel-root .Mui-active': {
                                color: theme.primary,
                                fontWeight: 'bold'
                            },
                            '& .MuiStepLabel-root .Mui-completed': {
                                color: theme.light
                            },
                        }}>
                        {steps.map((label) => (
                            <Step key={label}>
                                <StepLabel>{label}</StepLabel>
                            </Step>
                        ))}
                    </Stepper>

                    <Box sx={{ flex: 1, width: '100%', position: 'relative' }}>
                        {getStepContent(activeStep)}
                    </Box>

                    <Box sx={{
                        display: 'flex',
                        justifyContent: 'center',
                        gap: '20px',
                        width: '100%',
                        maxWidth: '600px',
                        padding: '20px 0'
                    }}>
                        <Button
                            variant="outlined"
                            disabled={activeStep === 0 || isLoading}
                            onClick={handleBack}
                            sx={{ ...buttonStyle, width: '45%' }}
                        >
                            Back
                        </Button>
                        <Button
                            variant="contained"
                            onClick={handleNext}
                            disabled={
                                isLoading ||
                                (activeStep === 0 && !cupType) ||
                                (activeStep === 1 && !flavor) ||
                                (activeStep === 2 && !waterQuantity)
                            }
                            sx={{ ...buttonStyle, width: '45%' }}
                        >
                            {activeStep === steps.length - 1 ? 'Finish' : 'Next'}
                        </Button>
                    </Box>
                </Box>
                <AnimatePresence>
                    {isLoading && <LoadingOverlay />}
                </AnimatePresence>
            </motion.div>
        </div>
    );
}

export default App;
