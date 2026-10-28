package
{
   import flash.display.Loader;
   import flash.display.Sprite;
   import flash.events.Event;
   import flash.net.URLRequest;
   import flash.system.ApplicationDomain;
   import flash.system.LoaderContext;

   import de.tosox.personal_spotted_alert.SpottedBulb;

   // Root of the markers movie in place of whatever markers app the battle
   // would have started (vanilla or another mod's), which it loads as its only
   // child. Both share one ApplicationDomain, so VehicleMarker.insertSymbol
   // can create SpottedBulb by name
   public class PersonalSpottedAlertRoot extends Sprite
   {
      // Loaded on our own if Python never says which app to wrap
      private static const DEFAULT_APP_SWF:String = "battleVehicleMarkersApp.swf";

      // mxmlc only compiles classes that are referenced from the main class
      private static const CLASSES:Array = [SpottedBulb];

      // Lets Python tell that the markers movie runs through this root
      public const isPersonalSpottedAlertRoot:Boolean = true;

      private var _loader:Loader = null;
      private var _appLoading:Boolean = false;

      public function PersonalSpottedAlertRoot()
      {
         super();
         this._loader = new Loader();
         addChild(this._loader);
         // Python calls loadApp right after creating the movie, before its
         // first frame; if that never happens, the markers still have to load
         addEventListener(Event.ENTER_FRAME, this.onFirstFrameHandler);
      }

      // Called from Python with the app the battle was about to start
      public function loadApp(url:String) : void
      {
         if(this._appLoading)
         {
            return;
         }
         this._appLoading = true;
         this._loader.load(new URLRequest(url), new LoaderContext(false, ApplicationDomain.currentDomain));
      }

      // Python resolves 'root.vehicleMarkersCanvas' once the wrapped app has
      // loaded its libraries and called back, so its content is there by then
      public function get vehicleMarkersCanvas() : Object
      {
         var app:Object = this._loader.content;
         return app != null ? app.vehicleMarkersCanvas : null;
      }

      private function onFirstFrameHandler(event:Event) : void
      {
         removeEventListener(Event.ENTER_FRAME, this.onFirstFrameHandler);
         this.loadApp(DEFAULT_APP_SWF);
      }
   }
}
