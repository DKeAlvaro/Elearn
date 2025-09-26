import os
import json
from typing import Optional, Callable
import flet as ft

try:
    # Only import Pyjnius on Android
    from jnius import autoclass, PythonJavaClass, java_method
    ANDROID_AVAILABLE = True
except ImportError:
    ANDROID_AVAILABLE = False
    print("Pyjnius not available - running in non-Android environment")

class BillingManager:
    """Manages Google Play Billing integration for in-app purchases"""
    
    def __init__(self):
        self.billing_client = None
        self.is_connected = False
        self.premium_product_id = "premium_unlock_5euro"
        self.purchase_callback: Optional[Callable] = None
        self.connection_callback: Optional[Callable] = None
        # Defer Android initialization to avoid startup crashes
        self.activity = None
        self.android_initialized = False
        
        # Do NOT call _init_android_classes() here to avoid early crashes on app start
        # It will be called lazily when the premium view initializes billing.
    
    def _init_android_classes(self):
        """Initialize Android classes using Pyjnius"""
        # Ensure we update the module-level flag when classes are unavailable
        global ANDROID_AVAILABLE
        try:
            # Get the main activity if environment variable is provided
            activity_host_class = os.getenv("MAIN_ACTIVITY_HOST_CLASS_NAME")
            if activity_host_class:
                activity_host = autoclass(activity_host_class)
                self.activity = activity_host.mActivity
            
            # Import Google Play Billing classes
            self.BillingClient = autoclass('com.android.billingclient.billing.BillingClient')
            self.BillingClientBuilder = autoclass('com.android.billingclient.billing.BillingClient$Builder')
            self.BillingResult = autoclass('com.android.billingclient.billing.BillingResult')
            self.Purchase = autoclass('com.android.billingclient.billing.Purchase')
            self.ProductDetails = autoclass('com.android.billingclient.billing.ProductDetails')
            self.QueryProductDetailsParams = autoclass('com.android.billingclient.billing.QueryProductDetailsParams')
            self.BillingFlowParams = autoclass('com.android.billingclient.billing.BillingFlowParams')
            
            self.android_initialized = True
            print("Android billing classes initialized successfully")
        except Exception as e:
            print(f"Error initializing Android classes: {e}")
            ANDROID_AVAILABLE = False
            self.android_initialized = False
    
    def initialize_billing_client(self, purchase_callback: Callable = None, connection_callback: Callable = None):
        """Initialize the Google Play Billing client"""
        if not ANDROID_AVAILABLE:
            print("Billing not available - not running on Android")
            return False
        
        # Lazily initialize Android classes
        if not self.android_initialized:
            self._init_android_classes()
        
        # Ensure activity and classes are available before proceeding
        if not ANDROID_AVAILABLE or not self.android_initialized or self.activity is None:
            print("Android billing not initialized or activity unavailable")
            return False
        
        self.purchase_callback = purchase_callback
        self.connection_callback = connection_callback
        
        try:
            # Create PurchasesUpdatedListener
            class PurchasesUpdatedListener(PythonJavaClass):
                __javainterfaces__ = ['com/android/billingclient/billing/PurchasesUpdatedListener']
                
                def __init__(self, billing_manager):
                    super().__init__()
                    self.billing_manager = billing_manager
                
                @java_method('(Lcom/android/billingclient/billing/BillingResult;Ljava/util/List;)V')
                def onPurchasesUpdated(self, billing_result, purchases):
                    self.billing_manager._handle_purchases_updated(billing_result, purchases)
            
            # Create BillingClientStateListener
            class BillingClientStateListener(PythonJavaClass):
                __javainterfaces__ = ['com/android/billingclient/billing/BillingClientStateListener']
                
                def __init__(self, billing_manager):
                    super().__init__()
                    self.billing_manager = billing_manager
                
                @java_method('(Lcom/android/billingclient/billing/BillingResult;)V')
                def onBillingSetupFinished(self, billing_result):
                    self.billing_manager._handle_billing_setup_finished(billing_result)
                
                @java_method('()V')
                def onBillingServiceDisconnected(self):
                    self.billing_manager._handle_billing_service_disconnected()
            
            # Create listeners
            self.purchases_listener = PurchasesUpdatedListener(self)
            self.state_listener = BillingClientStateListener(self)
            
            # Build BillingClient
            builder = self.BillingClient.newBuilder(self.activity)
            builder = builder.setListener(self.purchases_listener)
            builder = builder.enablePendingPurchases()
            self.billing_client = builder.build()
            
            # Start connection
            self.billing_client.startConnection(self.state_listener)
            
            print("Billing client initialization started")
            return True
            
        except Exception as e:
            print(f"Error initializing billing client: {e}")
            return False
    
    def _handle_billing_setup_finished(self, billing_result):
        """Handle billing client setup completion"""
        response_code = billing_result.getResponseCode()
        if response_code == self.BillingClient.BillingResponseCode.OK:
            self.is_connected = True
            print("Billing client connected successfully")
            if self.connection_callback:
                self.connection_callback(True)
        else:
            print(f"Billing setup failed with code: {response_code}")
            if self.connection_callback:
                self.connection_callback(False)
    
    def _handle_billing_service_disconnected(self):
        """Handle billing service disconnection"""
        self.is_connected = False
        print("Billing service disconnected - attempting reconnection")
        # Attempt to reconnect
        if self.billing_client:
            self.billing_client.startConnection(self.state_listener)
    
    def _handle_purchases_updated(self, billing_result, purchases):
        """Handle purchase updates"""
        response_code = billing_result.getResponseCode()
        
        if response_code == self.BillingClient.BillingResponseCode.OK and purchases:
            for purchase in purchases:
                self._process_purchase(purchase)
        elif response_code == self.BillingClient.BillingResponseCode.USER_CANCELED:
            print("Purchase canceled by user")
            if self.purchase_callback:
                self.purchase_callback(False, "Purchase canceled")
        else:
            print(f"Purchase failed with code: {response_code}")
            if self.purchase_callback:
                self.purchase_callback(False, f"Purchase failed: {response_code}")
    
    def _process_purchase(self, purchase):
        """Process a successful purchase"""
        try:
            product_id = purchase.getProducts().get(0)  # Get first product ID
            purchase_token = purchase.getPurchaseToken()
            
            if product_id == self.premium_product_id:
                # Verify and acknowledge the purchase
                if purchase.getPurchaseState() == self.Purchase.PurchaseState.PURCHASED:
                    if not purchase.isAcknowledged():
                        self._acknowledge_purchase(purchase_token)
                    
                    # Save premium status
                    self._save_premium_status(True)
                    
                    if self.purchase_callback:
                        self.purchase_callback(True, "Premium unlocked successfully!")
                    
                    print("Premium purchase processed successfully")
            
        except Exception as e:
            print(f"Error processing purchase: {e}")
            if self.purchase_callback:
                self.purchase_callback(False, f"Error processing purchase: {e}")
    
    def _acknowledge_purchase(self, purchase_token):
        """Acknowledge a purchase"""
        try:
            AcknowledgePurchaseParams = autoclass('com.android.billingclient.billing.AcknowledgePurchaseParams')
            
            params = AcknowledgePurchaseParams.newBuilder()
            params = params.setPurchaseToken(purchase_token)
            acknowledge_params = params.build()
            
            # Create acknowledge response listener
            class AcknowledgePurchaseResponseListener(PythonJavaClass):
                __javainterfaces__ = ['com/android/billingclient/billing/AcknowledgePurchaseResponseListener']
                
                @java_method('(Lcom/android/billingclient/billing/BillingResult;)V')
                def onAcknowledgePurchaseResponse(self, billing_result):
                    if billing_result.getResponseCode() == self.BillingClient.BillingResponseCode.OK:
                        print("Purchase acknowledged successfully")
                    else:
                        print(f"Purchase acknowledgment failed: {billing_result.getResponseCode()}")
            
            listener = AcknowledgePurchaseResponseListener()
            self.billing_client.acknowledgePurchase(acknowledge_params, listener)
            
        except Exception as e:
            print(f"Error acknowledging purchase: {e}")
    
    def launch_purchase_flow(self):
        """Launch the purchase flow for premium unlock"""
        if not ANDROID_AVAILABLE or not self.is_connected:
            print("Billing not available or not connected")
            return False
        
        try:
            # Query product details first
            Product = autoclass('com.android.billingclient.billing.QueryProductDetailsParams$Product')
            
            product = Product.newBuilder()
            product = product.setProductId(self.premium_product_id)
            product = product.setProductType(self.BillingClient.ProductType.INAPP)
            product_built = product.build()
            
            # Create product list
            ArrayList = autoclass('java.util.ArrayList')
            product_list = ArrayList()
            product_list.add(product_built)
            
            # Create query params
            query_params = self.QueryProductDetailsParams.newBuilder()
            query_params = query_params.setProductList(product_list)
            query_params_built = query_params.build()
            
            # Create product details response listener
            class ProductDetailsResponseListener(PythonJavaClass):
                __javainterfaces__ = ['com/android/billingclient/billing/ProductDetailsResponseListener']
                
                def __init__(self, billing_manager):
                    super().__init__()
                    self.billing_manager = billing_manager
                
                @java_method('(Lcom/android/billingclient/billing/BillingResult;Ljava/util/List;)V')
                def onProductDetailsResponse(self, billing_result, product_details_list):
                    if billing_result.getResponseCode() == self.billing_manager.BillingClient.BillingResponseCode.OK:
                        if product_details_list and product_details_list.size() > 0:
                            product_details = product_details_list.get(0)
                            self.billing_manager._launch_billing_flow(product_details)
                        else:
                            print("No product details found")
                    else:
                        print(f"Failed to get product details: {billing_result.getResponseCode()}")
            
            listener = ProductDetailsResponseListener(self)
            self.billing_client.queryProductDetailsAsync(query_params_built, listener)
            
            return True
            
        except Exception as e:
            print(f"Error launching purchase flow: {e}")
            return False
    
    def _launch_billing_flow(self, product_details):
        """Launch the actual billing flow with product details"""
        try:
            # Create billing flow params
            ProductDetailsParams = autoclass('com.android.billingclient.billing.BillingFlowParams$ProductDetailsParams')
            
            product_params = ProductDetailsParams.newBuilder()
            product_params = product_params.setProductDetails(product_details)
            product_params_built = product_params.build()
            
            # Create product list
            ArrayList = autoclass('java.util.ArrayList')
            product_params_list = ArrayList()
            product_params_list.add(product_params_built)
            
            # Create billing flow params
            billing_flow_params = self.BillingFlowParams.newBuilder()
            billing_flow_params = billing_flow_params.setProductDetailsParamsList(product_params_list)
            billing_flow_params_built = billing_flow_params.build()
            
            # Guard activity presence
            if self.activity is None:
                print("Cannot launch billing flow: activity is unavailable")
                return
            
            # Launch billing flow
            billing_result = self.billing_client.launchBillingFlow(self.activity, billing_flow_params_built)
            
            if billing_result.getResponseCode() != self.BillingClient.BillingResponseCode.OK:
                print(f"Failed to launch billing flow: {billing_result.getResponseCode()}")
            
        except Exception as e:
            print(f"Error in billing flow: {e}")
    
    def check_premium_status(self) -> bool:
        """Check if user has premium access"""
        # First check local storage
        if self._load_premium_status():
            return True
        
        # Then check with Google Play if connected
        if ANDROID_AVAILABLE and self.is_connected:
            self._query_purchases()
        
        return self._load_premium_status()
    
    def _query_purchases(self):
        """Query existing purchases from Google Play"""
        try:
            QueryPurchasesParams = autoclass('com.android.billingclient.billing.QueryPurchasesParams')
            
            params = QueryPurchasesParams.newBuilder()
            params = params.setProductType(self.BillingClient.ProductType.INAPP)
            query_params = params.build()
            
            # Create purchase response listener
            class PurchasesResponseListener(PythonJavaClass):
                __javainterfaces__ = ['com/android/billingclient/billing/PurchasesResponseListener']
                
                def __init__(self, billing_manager):
                    super().__init__()
                    self.billing_manager = billing_manager
                
                @java_method('(Lcom/android/billingclient/billing/BillingResult;Ljava/util/List;)V')
                def onQueryPurchasesResponse(self, billing_result, purchases):
                    if billing_result.getResponseCode() == self.billing_manager.BillingClient.BillingResponseCode.OK:
                        has_premium = False
                        for purchase in purchases:
                            product_id = purchase.getProducts().get(0)
                            if (product_id == self.billing_manager.premium_product_id and 
                                purchase.getPurchaseState() == self.billing_manager.Purchase.PurchaseState.PURCHASED):
                                has_premium = True
                                break
                        
                        self.billing_manager._save_premium_status(has_premium)
            
            listener = PurchasesResponseListener(self)
            self.billing_client.queryPurchasesAsync(query_params, listener)
            
        except Exception as e:
            print(f"Error querying purchases: {e}")
    
    def _save_premium_status(self, is_premium: bool):
        """Save premium status to local storage"""
        try:
            status_file = "premium_status.json"
            with open(status_file, 'w') as f:
                json.dump({"is_premium": is_premium}, f)
        except Exception as e:
            print(f"Error saving premium status: {e}")
    
    def _load_premium_status(self) -> bool:
        """Load premium status from local storage"""
        try:
            status_file = "premium_status.json"
            if os.path.exists(status_file):
                with open(status_file, 'r') as f:
                    data = json.load(f)
                    return data.get("is_premium", False)
        except Exception as e:
            print(f"Error loading premium status: {e}")
        return False
    
    def disconnect(self):
        """Disconnect from billing service"""
        if self.billing_client and self.is_connected:
            try:
                self.billing_client.endConnection()
                self.is_connected = False
                print("Billing client disconnected")
            except Exception as e:
                print(f"Error disconnecting billing client: {e}")

# Global billing manager instance
billing_manager = BillingManager()